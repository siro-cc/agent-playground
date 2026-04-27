from app.flow_engine import run_flow_pipeline
from scripts.cases_week4 import CASES


def main() -> None:
    passed_intent = 0
    passed_tool = 0
    passed_stage = 0

    for idx, case in enumerate(CASES, start=1):
        state = run_flow_pipeline(case["question"])

        ok_intent = state.intent == case["expected_intent"]
        ok_tool = state.tool_used == case["expected_tool"]
        ok_stage = state.current_stage == case["expected_stage_end"]

        if ok_intent:
            passed_intent += 1
        if ok_tool:
            passed_tool += 1
        if ok_stage:
            passed_stage += 1

        print("=" * 80)
        print(f"Case {idx}")
        print("Question      :", case["question"])
        print("Intent        :", state.intent)
        print("Tool          :", state.tool_used)
        print("Current Stage :", state.current_stage)
        print("History       :", state.history)
        print("Intent Pass   :", ok_intent)
        print("Tool Pass     :", ok_tool)
        print("Stage Pass    :", ok_stage)
        print("Final Answer  :", state.final_answer)
        print("Next Action   :", state.next_action)
        print("Error         :", state.error)

    print("=" * 80)
    print(f"Intent Score: {passed_intent}/{len(CASES)}")
    print(f"Tool Score  : {passed_tool}/{len(CASES)}")
    print(f"Stage Score : {passed_stage}/{len(CASES)}")


if __name__ == "__main__":
    main()