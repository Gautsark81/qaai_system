# File: run_full_test.py

from pipeline.signal_ingestion import SignalIngestionPipeline
from signal_engine import persist_model
from infra.streamer import Streamer


def main():
    pipeline = SignalIngestionPipeline()
    signals_df = pipeline.run()

    if signals_df.empty:
        print("❌ No signals generated. Check data availability.")
    else:
        print("✅ Signals generated:\n", signals_df.head())

        # Optional: Stream top signals
        try:
            streamer = Streamer()
            for _, row in signals_df.iterrows():
                streamer.publish(row["symbol"], row)
            print("✅ Signals streamed to Redis/MLflow.")
        except Exception as e:
            print("⚠️ Streamer skipped due to error:", e)

        # Save signals locally
        signals_df.to_excel("latest_signals.xlsx", index=False)
        print("✅ Signals saved to latest_signals.xlsx")

    # Save model
    persist_model()


if __name__ == "__main__":
    main()
