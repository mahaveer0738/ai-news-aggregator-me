import uvicorn
import sys

def main():
    """
    Main entry point for the production-ready AI News Aggregator.
    This starts the FastAPI application using Uvicorn.
    """
    # Allows passing port as an argument, defaults to 8000
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
            
    print(f"Starting AI News Aggregator API on port {port}...")
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=port, reload=True)

if __name__ == "__main__":
    main()
