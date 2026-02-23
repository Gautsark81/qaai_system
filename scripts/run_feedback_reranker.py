# File: scripts/run_feedback_reranker.py

from watchlist.feedback_re_ranker import FeedbackReRanker

if __name__ == "__main__":
    reranker = FeedbackReRanker(top_n=50)
    reranker.run()
    print("✅ Feedback-based watchlist re-ranking completed.")
