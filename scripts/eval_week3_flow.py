from app.agent import run_agent_flow
from scripts.cases_week3 import CASES


def main() -> None:
    passed_intent = 0
    passed_tool = 0

    for idx, case in enumerate(CASES, start=1):
        state = run_agent_flow(case["question"])

        ok_intent = state.intent == case["expected_intent"]
        ok_tool = state.tool_used == case["expected_tool"]

        if ok_intent:
            passed_intent += 1
        if ok_tool:
            passed_tool += 1

        print("=" * 60)
        print(f"Case {idx}")
        print("Question       :", case["question"])
        print("Expected Intent:", case["expected_intent"])
        print("Actual Intent  :", state.intent)
        print("Expected Tool  :", case["expected_tool"])
        print("Actual Tool    :", state.tool_used)
        print("Intent Pass    :", ok_intent)
        print("Tool Pass      :", ok_tool)
        print("Final Answer   :", state.final_answer)
        print("Next Action    :", state.next_action)
        print("Error          :", state.error)

    print("=" * 60)
    print(f"Intent Score: {passed_intent}/{len(CASES)}")
    print(f"Tool Score  : {passed_tool}/{len(CASES)}")


if __name__ == "__main__":
    main()