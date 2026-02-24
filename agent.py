import argparse
from modules.agent_core import summarize_file, plan_trip, maybe_send_email, export_plan_pdf

def run_summarize(args):
    result = summarize_file(args.input)
    print(result)
    if args.email:
        maybe_send_email(args.email, "Travel Summary", result)
        print(f"\n[+] Summary emailed to {args.email}")

def run_plan(args):
    itinerary, _ = plan_trip(
        city=args.city,
        start_date=args.start,
        days=args.days,
        user_id=args.user,
        vibe=args.vibe or "",
        fast=args.fast,
    )
    print(itinerary)
    if args.email:
        subject = f"{args.days}-Day Travel Itinerary – {args.city} (from {args.start})"
        maybe_send_email(args.email, subject, itinerary)
        print(f"\n[+] Itinerary emailed to {args.email}")

def run_export_pdf(args):
    pdf_path, itinerary = export_plan_pdf(
        city=args.city,
        start_date=args.start,
        days=args.days,
        user_id=args.user,
        vibe=args.vibe or "",
        fast=args.fast,
    )
    print(itinerary)
    print(f"[+] PDF generated: {pdf_path}")

def main():
    parser = argparse.ArgumentParser(description="AI Travel Operations Agent (CLI)")
    sub = parser.add_subparsers(dest="command")

    p_sum = sub.add_parser("summarize", help="Summarize a booking PDF or ticket image")
    p_sum.add_argument("input", help="Path to PDF/image")
    p_sum.add_argument("--email", default=None)
    p_sum.set_defaults(func=run_summarize)

    p_plan = sub.add_parser("plan", help="Plan a trip")
    p_plan.add_argument("--city", required=True)
    p_plan.add_argument("--start", required=True, help="YYYY-MM-DD")
    p_plan.add_argument("--days", required=True, type=int)
    p_plan.add_argument("--user", default="default")
    p_plan.add_argument("--vibe", default="")
    p_plan.add_argument("--fast", action="store_true")
    p_plan.add_argument("--email", default=None)
    p_plan.set_defaults(func=run_plan)

    p_pdf = sub.add_parser("export-pdf", help="Plan trip and export itinerary PDF with place photos")
    p_pdf.add_argument("--city", required=True)
    p_pdf.add_argument("--start", required=True)
    p_pdf.add_argument("--days", required=True, type=int)
    p_pdf.add_argument("--user", default="default")
    p_pdf.add_argument("--vibe", default="")
    p_pdf.add_argument("--fast", action="store_true")
    p_pdf.set_defaults(func=run_export_pdf)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    args.func(args)

if __name__ == "__main__":
    main()
