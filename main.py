from dotenv import load_dotenv

load_dotenv()

from src.backend.multi_agent.agent import MultiAgent  # noqa: E402


if __name__ == "__main__":
    agent = MultiAgent()
    final_state = agent("Запусти полный ML-пайплайн на датасете fake_job_postings.")
    if final_state.final_report:
        print(f"\nReport markdown: {final_state.final_report.report_md_path}")
        print(f"Report JSON:     {final_state.final_report.report_json_path}")
        print("\nExecutive summary:")
        print(final_state.final_report.executive_summary)
        print("\nKey findings:")
        for kf in final_state.final_report.key_findings:
            print(f"  - {kf}")
    else:
        print("\nFinal report is missing. Errors:")
        for e in final_state.errors:
            print(f"  [{e.agent}] {e.message}")

    if final_state.data_scientist_report:
        ds = final_state.data_scientist_report
        print(f"\nBest model: {ds.best_model.model_name}")
        print(f"Test metrics: {ds.best_model.test_metrics}")
        print(f"Saved to: {ds.best_model_path}")

    print(f"\nSupervisor iterations: {final_state.iteration}")
