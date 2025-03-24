if __name__ == "__main__":
    from dotenv import load_dotenv
    import uvicorn
    load_dotenv()
    uvicorn.run(
        "web.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )