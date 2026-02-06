import os
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings 
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
import os
load_dotenv()

# ---------------- Utility ----------------
import random
from youtube_transcript_api import YouTubeTranscriptApi

import yt_dlp
import requests
from urllib.parse import urlparse, parse_qs

def extract_video_id(youtube_url: str) -> str:
    """Extract video ID from YouTube URL"""
    parsed = urlparse(youtube_url)
    if "youtube.com" in parsed.netloc:
        return parse_qs(parsed.query).get("v", [None])[0]
    if "youtu.be" in parsed.netloc:
        return parsed.path.lstrip("/")
    raise ValueError("Invalid YouTube URL")

def get_transcript(youtube_url: str) -> str:
    """yt-dlp transcript extraction - Works 95% without auth"""
    
    ydl_opts = {
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'skip_download': True,  # Just get metadata
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            
        # Try manual subtitles first (higher quality)
        if 'subtitles' in info and 'en' in info['subtitles']:
            subtitle_url = info['subtitles']['en'][0]['url']
            response = requests.get(subtitle_url, timeout=10)
            return response.text
            
        # Try auto-generated captions
        elif 'automatic_captions' in info and 'en' in info['automatic_captions']:
            subtitle_url = info['automatic_captions']['en'][0]['url']
            response = requests.get(subtitle_url, timeout=10)
            return response.text
            
        raise RuntimeError("No English captions available")
        
    except Exception as e:
        print(f"yt-dlp error: {e}")
        raise RuntimeError(f"Could not extract transcript: {str(e)}")



# ---------------- RAG Chain ----------------
def format_docs(docs):
    """Format retrieved documents into a single string"""
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain(youtube_url: str):
    """Build RAG chain for YouTube Q&A"""
    
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # 1. Get transcript
    transcript = get_transcript(youtube_url)
    
    # 2. Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.create_documents([transcript])
    
    # 3. Create embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=api_key
    )
    
    # 4. Create vector store
    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    
    # 5. Setup LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7
    )
    
    # 6. Create prompt
    prompt = PromptTemplate(
        template="""Answer based on the context from the YouTube video.

Context: {context}

Question: {question}

Answer:""",
        input_variables=["context", "question"]
    )
    
    # 7. Build chain
    chain = RunnableParallel({
        "context": retriever | RunnableLambda(format_docs),
        "question": RunnablePassthrough()
    })
    
    return chain | prompt | llm | StrOutputParser()