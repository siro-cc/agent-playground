from collections import defaultdict
from pathlib import Path

from app.agent import run_agent
from scripts.cases_week2 import CASES


def main() -> None:
    passed = 0
    category_total = defaultdict(int)
    category_passed = defaultdict(int)

    lines = []
    lines.append("# Week 2 Manual Eval Report")
    lines.append("")

    for idx, case in enumerate(CASES, start=1):
        resp = run_agent(case["question"])
        ok = resp.tool_used == case["expected_tool"]

        category = case["category"]
        category_total[category] += 1
        if ok:
            passed += 1
            category_passed[category] += 1

        print("=" * 80)
        print(f"Case {idx}")
        print("Category      :", category)
        print("Question      :", case["question"])
        print("Expected Tool :", case["expected_tool"])
        print("Actual Tool   :", resp.tool_used)
        print("Pass          :", ok)
        print("Error         :", resp.error)
        print("Final Answer  :", resp.final_answer)

        lines.append(f"## Case {idx}")
        lines.append(f"- Category: {category}")
        lines.append(f"- Question: {case['question']}")
        lines.append(f"- Expected Tool: {case['expected_tool']}")
        lines.append(f"- Actual Tool: {resp.tool_used}")
        lines.append(f"- Pass: {ok}")
        lines.append(f"- Error: {resp.error}")
        lines.append("")

    score_line = f"Overall Score: {passed}/{len(CASES)}"
    print("=" * 80)
    print(score_line)

    lines.append("# Summary")
    lines.append("")
    lines.append(f"- {score_line}")
    lines.append("")

    for category, total in category_total.items():
        cat_score = category_passed[category]
        summary = f"- {category}: {cat_score}/{total}"
        print(summary)
        lines.append(summary)

    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)

    report_path = report_dir / "week2_manual_eval_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()