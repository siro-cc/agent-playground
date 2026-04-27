from app.flow_engine import run_flow_pipeline
from scripts.cases_week4_v2 import CASES


def main() -> None:
    passed = 0

    for idx, case in enumerate(CASES, start=1):
        state = run_flow_pipeline(
            question=case["question"],
            approved=case["approved"],
        )

        ok_stage = state.current_stage == case["expected_stage_end"]
        ok_approval = state.requires_approval == case["expected_requires_approval"]
        ok = ok_stage and ok_approval

        if ok:
            passed += 1

        print("=" * 80)
        print(f"Case {idx}")
        print("Question            :", case["question"])
        print("Approved            :", case["approved"])
        print("Current Stage       :", state.current_stage)
        print("Requires Approval   :", state.requires_approval)
        print("Approved in State   :", state.approved)
        print("Stage Pass          :", ok_stage)
        print("Approval Pass       :", ok_approval)
        print("Overall Pass        :", ok)
        print("Final Answer        :", state.final_answer)
        print("Next Action         :", state.next_action)
        print("Error               :", state.error)
        print("History             :", [item.model_dump() for item in state.history])

    print("=" * 80)
    print(f"Score: {passed}/{len(CASES)}")


if __name__ == "__main__":
    main()