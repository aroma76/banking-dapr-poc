import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

def build_timesheet():
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # Styles
    font_title = Font(name="Segoe UI", size=15, bold=True, color="FFFFFF")
    font_subtitle = Font(name="Segoe UI", size=10, bold=True, color="E2E8F0")
    font_sec_hdr = Font(name="Segoe UI", size=11, bold=True, color="1A365D")
    font_tbl_hdr = Font(name="Segoe UI", size=10, bold=True, color="FFFFFF")
    font_body = Font(name="Segoe UI", size=9, bold=False, color="1A202C")
    font_body_bold = Font(name="Segoe UI", size=9, bold=True, color="1A202C")
    font_body_muted = Font(name="Segoe UI", size=8.5, bold=False, color="4A5568")
    font_total = Font(name="Segoe UI", size=10, bold=True, color="1A365D")

    fill_title = PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid")
    fill_subhdr = PatternFill(start_color="2B6CB0", end_color="2B6CB0", fill_type="solid")
    fill_sec_hdr = PatternFill(start_color="EBF8FF", end_color="EBF8FF", fill_type="solid")
    fill_tbl_hdr = PatternFill(start_color="2B6CB0", end_color="2B6CB0", fill_type="solid")
    fill_zebra = PatternFill(start_color="F7FAFC", end_color="F7FAFC", fill_type="solid")
    fill_white = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    fill_total = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")

    status_styles = {
        "DONE": (PatternFill(start_color="DEF7EC", end_color="DEF7EC", fill_type="solid"), Font(name="Segoe UI", size=8.5, bold=True, color="03543F")),
        "IN PROGRESS": (PatternFill(start_color="FEF08A", end_color="FEF08A", fill_type="solid"), Font(name="Segoe UI", size=8.5, bold=True, color="854D0E")),
        "TO DO": (PatternFill(start_color="E0E7FF", end_color="E0E7FF", fill_type="solid"), Font(name="Segoe UI", size=8.5, bold=True, color="3730A3")),
        "MILESTONE": (PatternFill(start_color="FCE7F3", end_color="FCE7F3", fill_type="solid"), Font(name="Segoe UI", size=8.5, bold=True, color="9D174D")),
        "DEADLINE": (PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid"), Font(name="Segoe UI", size=8.5, bold=True, color="991B1B")),
        "HIGH": (PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid"), Font(name="Segoe UI", size=8.5, bold=True, color="991B1B")),
        "CRITICAL": (PatternFill(start_color="FED7AA", end_color="FED7AA", fill_type="solid"), Font(name="Segoe UI", size=8.5, bold=True, color="9A3412")),
        "MEDIUM": (PatternFill(start_color="E0E7FF", end_color="E0E7FF", fill_type="solid"), Font(name="Segoe UI", size=8.5, bold=True, color="3730A3")),
    }

    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )
    total_border = Border(
        left=Side(style='thin', color='CBD5E0'),
        right=Side(style='thin', color='CBD5E0'),
        top=Side(style='thin', color='4A5568'),
        bottom=Side(style='double', color='1A365D')
    )

    # =========================================================================
    # SHEET 1: Executive Summary
    # =========================================================================
    ws1 = wb.create_sheet(title="Executive Summary")
    ws1.views.sheetView[0].showGridLines = True

    # Title & Subtitle
    ws1.merge_cells("A1:G1")
    ws1["A1"].value = "BANKING MICROSERVICES POC — TIMESHEET & DATE DELIVERY PLAN"
    ws1["A1"].font = font_title
    ws1["A1"].fill = fill_title
    ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[1].height = 36

    ws1.merge_cells("A2:G2")
    ws1["A2"].value = "Java Spring Boot  |  PostgreSQL  |  Dapr Service Invocation  |  Docker Compose (6 Containers)  |  Concurrency Control"
    ws1["A2"].font = font_subtitle
    ws1["A2"].fill = fill_subhdr
    ws1["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[2].height = 22

    # Section 1: Project Scope & Goal
    ws1.merge_cells("A4:G4")
    ws1["A4"].value = "1. PROJECT GOAL & SCOPE (SIMPLE 2-MICROSERVICE POC)"
    ws1["A4"].font = font_sec_hdr
    ws1["A4"].fill = fill_sec_hdr
    ws1["A4"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws1.row_dimensions[4].height = 24

    context_rows = [
        ("Project Objective", "Build a lightweight 2-microservice banking system to demonstrate how Dapr connects microservices and how database locking stops money from dropping below zero during simultaneous withdrawals."),
        ("Microservice 1: Transaction Service", "Spring Boot app (port 8081). Receives withdrawal requests from Postman or browser, validates inputs, and sends the request to Accounting Service via Dapr."),
        ("Microservice 2: Accounting Service", "Spring Boot app (port 8082). Only service with PostgreSQL access. Checks account balance, locks the account row during deduction, and logs transaction history."),
        ("Step 1: Direct HTTP Baseline", "First, services communicated directly (http://accounting-app:8082). This proved that the withdrawal math and JSON responses worked before adding extra tools."),
        ("Step 2: Dapr Service Invocation", "Next, services were upgraded to Dapr (http://localhost:3500/v1.0/invoke/accounting-service/method/...). Neither service hardcodes the other's IP or port."),
        ("Docker Parting Out (6 Containers)", "The system runs smoothly in Docker Compose parted into 6 containers: 1 PostgreSQL, 1 Dapr placement directory, 2 Spring Boot apps, and 2 Dapr sidecars."),
        ("Concurrency & Safety Goal", "Ensure that if 2 withdrawal requests arrive at the exact same second for the same account, the balance NEVER drops below zero and no money is lost.")
    ]

    r_idx = 5
    for title, desc in context_rows:
        ws1.row_dimensions[r_idx].height = 26
        c_title = ws1.cell(r_idx, 1, title)
        c_title.font = font_body_bold
        c_title.fill = fill_zebra
        c_title.border = thin_border
        c_title.alignment = Alignment(horizontal="left", vertical="center", indent=1)

        ws1.merge_cells(start_row=r_idx, start_column=2, end_row=r_idx, end_column=7)
        c_desc = ws1.cell(r_idx, 2, desc)
        c_desc.font = font_body
        c_desc.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        for c in range(2, 8):
            cell = ws1.cell(r_idx, c)
            cell.border = thin_border
            cell.fill = fill_white if (r_idx % 2 == 1) else fill_zebra
        r_idx += 1

    # Section 2: Schedule Metrics (Date-Based)
    r_idx += 1
    ws1.merge_cells(f"A{r_idx}:G{r_idx}")
    ws1[f"A{r_idx}"].value = "2. KEY DATES & DELIVERY MILESTONES (COMPLETION UNDER SEP 25, 2026)"
    ws1[f"A{r_idx}"].font = font_sec_hdr
    ws1[f"A{r_idx}"].fill = fill_sec_hdr
    ws1[f"A{r_idx}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws1.row_dimensions[r_idx].height = 24
    r_idx += 1

    metrics_rows = [
        ("Project Period", "Sep 15, 2026 – Sep 25, 2026", "Tracking Format", "Date-based milestones (No hourly clocking)"),
        ("Working Days", "9 Working Days (Tue Sep 15 to Fri Sep 25)", "Target Handover", "On or before Sep 25, 2026"),
        ("Week 1 Milestone", "Sep 18, 2026 (Friday) — Direct HTTP & Dapr invocation working cleanly", "Week 2 Milestone", "Sep 21, 2026 (Monday) — Concurrency protection & audit history tested"),
        ("Final Demo & Handover", "Sep 25, 2026 (Friday) — Senior walkthrough (Rajeev Ranjan) & sign-off", "Current Status", "ON TRACK (Ready for Sep 25, 2026)")
    ]

    for m in metrics_rows:
        ws1.row_dimensions[r_idx].height = 22
        c1 = ws1.cell(r_idx, 1, m[0])
        c1.font = font_body_bold
        c1.fill = fill_zebra
        c1.border = thin_border
        c1.alignment = Alignment(horizontal="left", vertical="center", indent=1)

        ws1.merge_cells(start_row=r_idx, start_column=2, end_row=r_idx, end_column=3)
        c2 = ws1.cell(r_idx, 2, m[1])
        c2.font = font_body
        c2.border = thin_border
        c2.alignment = Alignment(horizontal="left", vertical="center")
        ws1.cell(r_idx, 3).border = thin_border

        c3 = ws1.cell(r_idx, 4, m[2])
        c3.font = font_body_bold
        c3.fill = fill_zebra
        c3.border = thin_border
        c3.alignment = Alignment(horizontal="left", vertical="center", indent=1)

        ws1.merge_cells(start_row=r_idx, start_column=5, end_row=r_idx, end_column=7)
        c4 = ws1.cell(r_idx, 5, m[3])
        c4.font = font_body
        c4.border = thin_border
        c4.alignment = Alignment(horizontal="left", vertical="center")
        for c in range(5, 8):
            ws1.cell(r_idx, c).border = thin_border
        r_idx += 1

    # Section 3: Delivery Roadmap Phases
    r_idx += 1
    ws1.merge_cells(f"A{r_idx}:G{r_idx}")
    ws1[f"A{r_idx}"].value = "3. DELIVERY ROADMAP PHASES (9-DAY DATE TIMELINE)"
    ws1[f"A{r_idx}"].font = font_sec_hdr
    ws1[f"A{r_idx}"].fill = fill_sec_hdr
    ws1[f"A{r_idx}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws1.row_dimensions[r_idx].height = 24
    r_idx += 1

    phase_headers = ["Phase", "Date", "Simple Goal", "Key Deliverables", "Status"]
    ws1.row_dimensions[r_idx].height = 22
    for c_i, h in enumerate(phase_headers, 1):
        if c_i == 3:
            ws1.merge_cells(start_row=r_idx, start_column=3, end_row=r_idx, end_column=4)
            c = ws1.cell(r_idx, 3, h)
            ws1.cell(r_idx, 4).fill = fill_tbl_hdr
            ws1.cell(r_idx, 4).border = thin_border
        elif c_i == 4:
            ws1.merge_cells(start_row=r_idx, start_column=5, end_row=r_idx, end_column=6)
            c = ws1.cell(r_idx, 5, h)
            ws1.cell(r_idx, 6).fill = fill_tbl_hdr
            ws1.cell(r_idx, 6).border = thin_border
        elif c_i == 5:
            c = ws1.cell(r_idx, 7, h)
        else:
            c = ws1.cell(r_idx, c_i, h)
        c.font = font_tbl_hdr
        c.fill = fill_tbl_hdr
        c.border = thin_border
        c.alignment = Alignment(horizontal="center", vertical="center")
    r_idx += 1

    phases = [
        ("Phase 1: Project Creation", "Sep 15 (Tue)", "Create Spring Boot projects for Transaction & Accounting services", "Both services created, configured, and compile cleanly", "DONE"),
        ("Phase 2: Docker Setup", "Sep 16 (Wed)", "Part out 6 Docker containers (database, apps, sidecars, placement)", "docker-compose.yml running, 6 containers green, seed accounts ready", "IN PROGRESS"),
        ("Phase 3: Communication Progression", "Sep 17 (Thu)", "First connect via direct HTTP, verify it works, then upgrade to Dapr", "Direct HTTP tested, Dapr invocation working, duplicate check enabled", "TO DO"),
        ("Phase 4: Concurrency Lock & Testing", "Sep 18 (Fri)", "Add SELECT FOR UPDATE row locking and test overdraft protection", "Database locking in repository, Week 1 progress check complete", "MILESTONE"),
        ("Phase 5: Concurrency Verification", "Sep 21 (Mon)", "Test simultaneous withdrawals to verify balance never goes below zero", "Concurrency test script verified, DB audit logs accurate", "TO DO"),
        ("Phase 6: Code Cleanup & Logs", "Sep 22 (Tue)", "Clean up code and add simple, friendly console logs", "Clean codebase, clear logs showing Dapr hops & balance deductions", "TO DO"),
        ("Phase 7: Simple Documentation", "Sep 23 (Wed)", "Write easy README with clear startup steps and architecture diagram", "README.md ready with clear commands for anyone to test", "TO DO"),
        ("Phase 8: Cold Restart & Demo Practice", "Sep 24 (Thu)", "Test clean cold startup in Docker and rehearse walkthrough talking points", "5/5 test cases passing, 1-page demo talking points sheet", "TO DO"),
        ("Phase 9: Live Demo & Handover", "Sep 25 (Fri)", "Live demo presentation to senior (Rajeev Ranjan) and project sign-off", "Live demo completed, final project handover under date Sep 25", "DEADLINE")
    ]

    for p in phases:
        ws1.row_dimensions[r_idx].height = 24
        c1 = ws1.cell(r_idx, 1, p[0])
        c1.font = font_body_bold
        c1.border = thin_border
        c1.alignment = Alignment(horizontal="left", vertical="center", indent=1)

        c2 = ws1.cell(r_idx, 2, p[1])
        c2.font = font_body
        c2.border = thin_border
        c2.alignment = Alignment(horizontal="center", vertical="center")

        ws1.merge_cells(start_row=r_idx, start_column=3, end_row=r_idx, end_column=4)
        c3 = ws1.cell(r_idx, 3, p[2])
        c3.font = font_body
        c3.border = thin_border
        c3.alignment = Alignment(horizontal="left", vertical="center")
        ws1.cell(r_idx, 4).border = thin_border

        ws1.merge_cells(start_row=r_idx, start_column=5, end_row=r_idx, end_column=6)
        c4 = ws1.cell(r_idx, 5, p[3])
        c4.font = font_body
        c4.border = thin_border
        c4.alignment = Alignment(horizontal="left", vertical="center")
        ws1.cell(r_idx, 6).border = thin_border

        c5 = ws1.cell(r_idx, 7, p[4])
        st_fill, st_font = status_styles.get(p[4], (fill_white, font_body))
        c5.fill = st_fill
        c5.font = st_font
        c5.border = thin_border
        c5.alignment = Alignment(horizontal="center", vertical="center")
        r_idx += 1

    ws1.column_dimensions['A'].width = 32
    ws1.column_dimensions['B'].width = 16
    ws1.column_dimensions['C'].width = 24
    ws1.column_dimensions['D'].width = 24
    ws1.column_dimensions['E'].width = 24
    ws1.column_dimensions['F'].width = 24
    ws1.column_dimensions['G'].width = 16

    # =========================================================================
    # SHEET 2: Day-by-Day Timesheet (Date-based, No clock time slots)
    # =========================================================================
    ws2 = wb.create_sheet(title="Day-by-Day Timesheet")
    ws2.views.sheetView[0].showGridLines = True

    ws2.merge_cells("A1:G1")
    ws2["A1"].value = "DAILY TIMESHEET & DATE-BASED WORK PLAN (SEP 15 – SEP 25, 2026)"
    ws2["A1"].font = font_title
    ws2["A1"].fill = fill_title
    ws2["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws2.row_dimensions[1].height = 36

    headers2 = ["Date", "Day", "Phase", "Task ID", "Task Description (Simple Language)", "Expected Deliverable", "Status"]
    ws2.row_dimensions[2].height = 24
    for c_i, h in enumerate(headers2, 1):
        c = ws2.cell(2, c_i, h)
        c.font = font_tbl_hdr
        c.fill = fill_tbl_hdr
        c.border = thin_border
        c.alignment = Alignment(horizontal="center", vertical="center")

    daily_tasks = [
        # Day 1: Sep 15 (Tue)
        ("15-Sep-2026", "Tuesday", "Learn", "T01", "Learn POC goals & how Dapr connects microservices without hardcoded URLs", "Architecture notes & clear mental model", "DONE"),
        ("15-Sep-2026", "Tuesday", "Setup", "T02", "Check prerequisites on local PC: Java 17, Docker Desktop, Maven, and IDE", "Development environment ready", "DONE"),
        ("15-Sep-2026", "Tuesday", "Code", "T03", "Create Transaction Service: handles client withdrawal requests (port 8081)", "transaction-service project created", "DONE"),
        ("15-Sep-2026", "Tuesday", "Code", "T04", "Create Accounting Service: checks balances & deducts money from DB (port 8082)", "accounting-service project created", "DONE"),
        ("15-Sep-2026", "Tuesday", "Code", "T05", "Configure application properties: port 8081 for Transaction, port 8082 for Accounting", "application.yml files written for both services", "DONE"),
        ("15-Sep-2026", "Tuesday", "Code", "T06", "Verify Maven compilation locally to ensure zero syntax or dependency errors", "Both microservices build cleanly with Maven", "DONE"),

        # Day 2: Sep 16 (Wed)
        ("16-Sep-2026", "Wednesday", "Setup", "T07", "Write simple Dockerfiles to containerize both Java services", "Dockerfiles added to both service folders", "IN PROGRESS"),
        ("16-Sep-2026", "Wednesday", "Setup", "T08", "Set up Docker Compose with PostgreSQL database (5432) and Dapr discovery (50005)", "banking-postgres and dapr-placement configured", "IN PROGRESS"),
        ("16-Sep-2026", "Wednesday", "Setup", "T09", "Add starter bank accounts in PostgreSQL: ACC001 (₹5,000) and ACC002 (₹10,000)", "Starter accounts created via database/init.sql", "IN PROGRESS"),
        ("16-Sep-2026", "Wednesday", "Setup", "T10", "Attach Dapr sidecars to each service in Docker Compose using shared network mode", "Sidecars (transaction-dapr, accounting-dapr) mapped", "TO DO"),
        ("16-Sep-2026", "Wednesday", "Setup", "T11", "Start all 6 containers with docker compose up and verify they run healthy", "All 6 containers running green in Docker Desktop", "TO DO"),

        # Day 3: Sep 17 (Thu)
        ("17-Sep-2026", "Thursday", "Code", "T12", "Step 1 (Direct HTTP): Connect services directly via HTTP to confirm basic math works", "Verified direct REST communication works", "TO DO"),
        ("17-Sep-2026", "Thursday", "Code", "T13", "Write withdrawal logic in Accounting Service: check account exists & balance is enough", "Core withdrawal balance deduction implemented", "TO DO"),
        ("17-Sep-2026", "Thursday", "Code", "T14", "Step 2 (Dapr Upgrade): Switch from direct HTTP to Dapr Service Invocation", "Services fully decoupled via Dapr sidecars", "TO DO"),
        ("17-Sep-2026", "Thursday", "Code", "T15", "Add duplicate request check (Idempotency): check requestId to prevent double-charging", "Duplicate withdrawal protection enabled", "TO DO"),
        ("17-Sep-2026", "Thursday", "Test", "T16", "Manual test: withdraw ₹500 from ACC001 via cURL, confirm balance becomes ₹4,500", "First successful withdrawal verified end-to-end", "TO DO"),

        # Day 4: Sep 18 (Fri)
        ("18-Sep-2026", "Friday", "Learn", "T17", "Learn why simultaneous withdrawals cause negative balance (race conditions)", "Clear understanding of concurrent banking issues", "TO DO"),
        ("18-Sep-2026", "Friday", "Code", "T18", "Add database row lock (SELECT FOR UPDATE) so simultaneous requests wait their turn", "Row-level locking implemented in database layer", "TO DO"),
        ("18-Sep-2026", "Friday", "Test", "T19", "Test overdraft: try withdrawing ₹10,000 when balance is ₹4,500 (verify clean error)", "Verified balance remains untouched on overdraft", "TO DO"),
        ("18-Sep-2026", "Friday", "Test", "T20", "Test wrong account: try withdrawing from non-existent ACC999 (verify 404 response)", "Error handling for non-existent accounts verified", "TO DO"),
        ("18-Sep-2026", "Friday", "Review", "T21", "Week 1 check: confirm all code compiles, restart Docker cleanly, draft notes for mentor", "Week 1 baseline achieved & verified", "MILESTONE"),

        # Day 5: Sep 21 (Mon)
        ("21-Sep-2026", "Monday", "Test", "T22", "Write a simple script (test-poc.ps1) to send 2 withdrawal requests at the exact same second", "Automated test script for concurrency", "TO DO"),
        ("21-Sep-2026", "Monday", "Test", "T23", "Run concurrency test: two ₹3,000 requests on ₹5,000 balance (1 passes, 1 fails, balance ₹2,000)", "Confirmed: balance never drops below zero", "TO DO"),
        ("21-Sep-2026", "Monday", "Test", "T24", "Test duplicate requests sent at once: verify identical requestId is safely blocked", "Verified unique requestId prevents double deduction", "TO DO"),
        ("21-Sep-2026", "Monday", "Test", "T25", "Inspect PostgreSQL database: check withdrawal_transactions table for complete audit log", "Database transaction history verified accurate", "TO DO"),

        # Day 6: Sep 22 (Tue)
        ("22-Sep-2026", "Tuesday", "Code", "T26", "Clean up code: remove unused imports, format files, make code easy to read", "Clean, readable code in both services", "TO DO"),
        ("22-Sep-2026", "Tuesday", "Code", "T27", "Add friendly console logs showing step-by-step progress during each request", "Console logs are easy to follow during demo", "TO DO"),
        ("22-Sep-2026", "Tuesday", "Test", "T28", "Re-run all tests to confirm clean code did not break any functionality", "All tests passing on cleaned code", "TO DO"),
        ("22-Sep-2026", "Tuesday", "Setup", "T29", "Check Swagger UI on both services (ports 8081 & 8082) for interactive visual testing", "Interactive Swagger UI available in browser", "TO DO"),

        # Day 7: Sep 23 (Wed)
        ("23-Sep-2026", "Wednesday", "Docs", "T30", "Write simple README.md: project overview, prerequisites, and how to run with Docker", "Easy-to-follow README.md documentation", "TO DO"),
        ("23-Sep-2026", "Wednesday", "Docs", "T31", "Draw visual diagram showing: User -> Transaction -> Dapr -> Accounting -> PostgreSQL", "Visual architecture flow included in README", "TO DO"),
        ("23-Sep-2026", "Wednesday", "Test", "T32", "Follow README instructions from scratch to ensure anyone can run the project easily", "Verified documentation works without missing steps", "TO DO"),
        ("23-Sep-2026", "Wednesday", "Docs", "T33", "Clean up repository: check .gitignore, remove temporary test files", "Clean repository ready for review", "TO DO"),

        # Day 8: Sep 24 (Thu)
        ("24-Sep-2026", "Thursday", "Test", "T34", "Cold restart test: test 'docker compose down -v' then 'docker compose up' from zero", "Verified fresh bootstrap works smoothly", "TO DO"),
        ("24-Sep-2026", "Thursday", "Test", "T35", "Run complete 5-test checklist: normal withdrawal, duplicate, overdraft, missing account, concurrency", "5 out of 5 test scenarios verified 100% passing", "TO DO"),
        ("24-Sep-2026", "Thursday", "Demo", "T36", "Prepare 1-page talking points: simple explanations for 'Why Dapr?' and 'Why database locking?'", "1-page quick-reference sheet for senior demo", "TO DO"),
        ("24-Sep-2026", "Thursday", "Demo", "T37", "Practice demo walkthrough: rehearse explaining architecture, showing Docker, and running cURL", "Confident, clear walkthrough rehearsed", "TO DO"),

        # Day 9: Sep 25 (Fri)
        ("25-Sep-2026", "Friday", "Demo", "T38", "Morning system check: start Docker stack, confirm all 6 containers healthy, run 1 quick test", "System 100% ready for presentation", "TO DO"),
        ("25-Sep-2026", "Friday", "Demo", "T39", "LIVE POC DEMO TO SENIOR (Rajeev Ranjan): explain 2 microservices, Dapr, and concurrency safety", "Live demonstration successfully presented", "MILESTONE"),
        ("25-Sep-2026", "Friday", "Review", "T40", "Gather senior feedback and note down any suggestions or questions", "Demo feedback captured", "TO DO"),
        ("25-Sep-2026", "Friday", "Code", "T41", "Make any minor tweaks requested by senior during the demo", "Senior feedback items completed", "TO DO"),
        ("25-Sep-2026", "Friday", "Deliver", "T42", "Final project handover: share GitHub link, README, and timesheet with senior for sign-off", "Official Project Handover Complete (Under Sep 25)", "DEADLINE")
    ]

    r_idx = 3
    for row in daily_tasks:
        ws2.row_dimensions[r_idx].height = 20
        date_str, day_str, phase, t_id, desc, deliv, status = row

        is_zebra = (r_idx % 2 == 1)
        row_fill = fill_zebra if is_zebra else fill_white

        vals = [date_str, day_str, phase, t_id, desc, deliv, status]
        for c_i, v in enumerate(vals, 1):
            c = ws2.cell(r_idx, c_i, v)
            c.border = thin_border
            c.fill = row_fill
            if c_i in (1, 2, 4):
                c.alignment = Alignment(horizontal="center", vertical="center")
                c.font = font_body
            elif c_i == 3:
                c.alignment = Alignment(horizontal="center", vertical="center")
                c.font = font_body_bold
            elif c_i == 5:
                c.alignment = Alignment(horizontal="left", vertical="center")
                c.font = font_body
            elif c_i == 6:
                c.alignment = Alignment(horizontal="left", vertical="center")
                c.font = font_body_muted
            elif c_i == 7:
                st_fill, st_font = status_styles.get(status, (row_fill, font_body))
                c.fill = st_fill
                c.font = st_font
                c.alignment = Alignment(horizontal="center", vertical="center")
        r_idx += 1

    # Total Row
    ws2.row_dimensions[r_idx].height = 24
    ws2.merge_cells(start_row=r_idx, start_column=1, end_row=r_idx, end_column=4)
    ws2.cell(r_idx, 1, "TOTAL PROJECT TIMELINE:").font = font_total
    ws2.cell(r_idx, 1).alignment = Alignment(horizontal="right", vertical="center")
    for c_i in range(1, 5):
        ws2.cell(r_idx, c_i).border = total_border
        ws2.cell(r_idx, c_i).fill = fill_total

    ws2.merge_cells(start_row=r_idx, start_column=5, end_row=r_idx, end_column=7)
    ws2.cell(r_idx, 5, "9 Working Days (Sep 15 – Sep 25, 2026) · Target Completion Date: Sep 25, 2026").font = font_total
    ws2.cell(r_idx, 5).alignment = Alignment(horizontal="center", vertical="center")
    for c_i in range(5, 8):
        ws2.cell(r_idx, c_i).border = total_border
        ws2.cell(r_idx, c_i).fill = fill_total

    ws2.column_dimensions['A'].width = 14
    ws2.column_dimensions['B'].width = 13
    ws2.column_dimensions['C'].width = 12
    ws2.column_dimensions['D'].width = 10
    ws2.column_dimensions['E'].width = 62
    ws2.column_dimensions['F'].width = 46
    ws2.column_dimensions['G'].width = 16

    # =========================================================================
    # SHEET 3: Master Task WBS (15 Canonical Tasks, Date-Based)
    # =========================================================================
    ws3 = wb.create_sheet(title="Master Task WBS")
    ws3.views.sheetView[0].showGridLines = True

    ws3.merge_cells("A1:G1")
    ws3["A1"].value = "MASTER WORK BREAKDOWN STRUCTURE (WBS) — 15 POC TASKS"
    ws3["A1"].font = font_title
    ws3["A1"].fill = fill_title
    ws3["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws3.row_dimensions[1].height = 36

    headers3 = ["Task ID", "Task Name (Simple Language)", "Phase", "Target Date", "Priority", "Why It Matters (Simple Terms)", "Status"]
    ws3.row_dimensions[2].height = 24
    for c_i, h in enumerate(headers3, 1):
        c = ws3.cell(2, c_i, h)
        c.font = font_tbl_hdr
        c.fill = fill_tbl_hdr
        c.border = thin_border
        c.alignment = Alignment(horizontal="center", vertical="center")

    wbs_tasks = [
        ("T01", "Learn POC goals and understand Dapr sidecar basics", "Learn", "Day 1 (Sep 15)", "High", "Explains how microservices talk through sidecars without hardcoded IPs", "DONE"),
        ("T02", "Check prerequisites: Java 17, Docker Desktop, IDE", "Setup", "Day 1 (Sep 15)", "High", "Ensures computer is ready to run all 6 containers", "DONE"),
        ("T03", "Create Transaction Service Spring Boot project", "Code", "Day 1 (Sep 15)", "Critical", "Public endpoint that accepts withdrawal requests (/api/v1/transactions/withdraw)", "DONE"),
        ("T04", "Create Accounting Service Spring Boot project with JPA", "Code", "Day 1 (Sep 15)", "Critical", "Banking engine that checks balances & updates database", "DONE"),
        ("T05", "Write Dockerfiles & configure PostgreSQL database", "Setup", "Day 2 (Sep 16)", "Critical", "Initializes database schema and starter accounts (ACC001)", "IN PROGRESS"),
        ("T06", "Set up 6 containers in Docker Compose (apps + sidecars + placement)", "Setup", "Day 2 (Sep 16)", "Critical", "Connects sidecars and apps using shared network mode", "TO DO"),
        ("T07", "Step 1: Test Direct HTTP communication between microservices", "Code", "Day 3 (Sep 17)", "High", "Proves basic withdrawal calculation works before adding Dapr", "TO DO"),
        ("T08", "Step 2: Upgrade to Dapr Service Invocation & duplicate request check", "Code", "Day 3 (Sep 17)", "Critical", "Decouples services completely and prevents double deductions", "TO DO"),
        ("T09", "Add database row locking (SELECT ... FOR UPDATE) in repository", "Code", "Day 4 (Sep 18)", "Critical", "Locks account row so simultaneous requests wait in queue", "TO DO"),
        ("T10", "Manual testing: normal withdrawal, overdraft & non-existent account", "Test", "Day 4 (Sep 18)", "High", "Confirms proper responses (HTTP 200, 400, 404)", "TO DO"),
        ("T11", "Concurrency test: send 2 simultaneous withdrawals to verify balance", "Test", "Day 5 (Sep 21)", "Critical", "Proves balance never goes below zero during race conditions", "TO DO"),
        ("T12", "Clean up code, format files & add friendly console logs", "Code", "Day 6 (Sep 22)", "Medium", "Ensures console logs clearly show every transaction step", "TO DO"),
        ("T13", "Write simple README.md with startup steps & architecture diagram", "Docs", "Day 7 (Sep 23)", "High", "Provides clear instructions so anyone can run the POC easily", "TO DO"),
        ("T14", "End-to-end dry run: test cold start & prepare demo talking points", "Demo", "Day 8 (Sep 24)", "High", "Validates clean bootstrap and prepares answers for senior", "TO DO"),
        ("T15", "Live demo walkthrough with senior (Rajeev Ranjan) & project sign-off", "Demo", "Day 9 (Sep 25)", "Critical", "Demonstrates working POC and achieves official sign-off", "DEADLINE")
    ]

    r_idx = 3
    for row in wbs_tasks:
        ws3.row_dimensions[r_idx].height = 22
        t_id, name, phase, p_day, prio, conc_rel, status = row
        is_zebra = (r_idx % 2 == 1)
        row_fill = fill_zebra if is_zebra else fill_white

        vals = [t_id, name, phase, p_day, prio, conc_rel, status]
        for c_i, v in enumerate(vals, 1):
            c = ws3.cell(r_idx, c_i, v)
            c.border = thin_border
            c.fill = row_fill
            if c_i in (1, 3, 4):
                c.alignment = Alignment(horizontal="center", vertical="center")
                c.font = font_body
            elif c_i == 2:
                c.alignment = Alignment(horizontal="left", vertical="center")
                c.font = font_body_bold
            elif c_i == 5:
                p_fill, p_font = status_styles.get(prio.upper(), (row_fill, font_body))
                c.fill = p_fill
                c.font = p_font
                c.alignment = Alignment(horizontal="center", vertical="center")
            elif c_i == 6:
                c.alignment = Alignment(horizontal="left", vertical="center")
                c.font = font_body_muted
            elif c_i == 7:
                s_fill, s_font = status_styles.get(status, (row_fill, font_body))
                c.fill = s_fill
                c.font = s_font
                c.alignment = Alignment(horizontal="center", vertical="center")
        r_idx += 1

    ws3.row_dimensions[r_idx].height = 24
    ws3.merge_cells(start_row=r_idx, start_column=1, end_row=r_idx, end_column=3)
    ws3.cell(r_idx, 1, "TOTAL CORE POC TASKS:").font = font_total
    ws3.cell(r_idx, 1).alignment = Alignment(horizontal="right", vertical="center")
    for c_i in range(1, 4):
        ws3.cell(r_idx, c_i).border = total_border
        ws3.cell(r_idx, c_i).fill = fill_total

    ws3.merge_cells(start_row=r_idx, start_column=4, end_row=r_idx, end_column=7)
    ws3.cell(r_idx, 4, "15 Core Tasks · Target Handover Under Sep 25, 2026").font = font_total
    ws3.cell(r_idx, 4).alignment = Alignment(horizontal="center", vertical="center")
    for c_i in range(4, 8):
        ws3.cell(r_idx, c_i).border = total_border
        ws3.cell(r_idx, c_i).fill = fill_total

    ws3.column_dimensions['A'].width = 11
    ws3.column_dimensions['B'].width = 48
    ws3.column_dimensions['C'].width = 12
    ws3.column_dimensions['D'].width = 16
    ws3.column_dimensions['E'].width = 12
    ws3.column_dimensions['F'].width = 50
    ws3.column_dimensions['G'].width = 15

    # =========================================================================
    # SHEET 4: Concurrency & Docker Architecture
    # =========================================================================
    ws4 = wb.create_sheet(title="Concurrency & Test Plan")
    ws4.views.sheetView[0].showGridLines = True

    ws4.merge_cells("A1:G1")
    ws4["A1"].value = "CONCURRENCY, DOCKER & COMMUNICATION SPECIFICATION"
    ws4["A1"].font = font_title
    ws4["A1"].fill = fill_title
    ws4["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws4.row_dimensions[1].height = 36

    ws4.merge_cells("A2:G2")
    ws4["A2"].value = "Explaining Docker Containers, Direct HTTP vs Dapr Progression, and Database Row Locking"
    ws4["A2"].font = font_subtitle
    ws4["A2"].fill = fill_subhdr
    ws4["A2"].alignment = Alignment(horizontal="center", vertical="center")
    ws4.row_dimensions[2].height = 22

    # Part 1: Docker 6 Containers Table
    ws4.merge_cells("A4:G4")
    ws4["A4"].value = "1. DOCKER ARCHITECTURE — THE 6 CONTAINERS PARTED OUT"
    ws4["A4"].font = font_sec_hdr
    ws4["A4"].fill = fill_sec_hdr
    ws4["A4"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws4.row_dimensions[4].height = 24

    docker_headers = ["#", "Container Name", "Technology", "Port(s)", "Network Mode", "Purpose & Working Mechanism", ""]
    ws4.row_dimensions[5].height = 22
    for c_i, h in enumerate(docker_headers[:6], 1):
        if c_i == 6:
            ws4.merge_cells(start_row=5, start_column=6, end_row=5, end_column=7)
            c = ws4.cell(5, 6, "Purpose & Working Mechanism")
            ws4.cell(5, 7).fill = fill_tbl_hdr
            ws4.cell(5, 7).border = thin_border
        else:
            c = ws4.cell(5, c_i, h)
        c.font = font_tbl_hdr
        c.fill = fill_tbl_hdr
        c.border = thin_border
        c.alignment = Alignment(horizontal="center", vertical="center")

    docker_containers = [
        ("1", "banking-postgres", "PostgreSQL 15 Alpine", "5432:5432", "banking-net", "Database for accounts & transactions. Runs database/init.sql on startup to seed ACC001 (₹5,000)."),
        ("2", "dapr-placement", "daprio/dapr:1.13.0", "50005:50005", "banking-net", "Dapr placement & discovery service. Acts as the directory so sidecars discover each other without hardcoded IPs."),
        ("3", "transaction-app", "Spring Boot (Java 17)", "8081:8081", "banking-net", "Microservice 1: Receives client withdrawal requests, validates inputs, and calls Accounting via Dapr."),
        ("4", "transaction-dapr", "daprio/daprd:1.13.0", "3500 (HTTP)", "service:transaction-app", "Sidecar for Microservice 1: Shares network with transaction-app. Reached via localhost:3500."),
        ("5", "accounting-app", "Spring Boot (Java 17)", "8082:8082", "banking-net", "Microservice 2: Owns PostgreSQL database. Executes SELECT FOR UPDATE locking and balance deduction."),
        ("6", "accounting-dapr", "daprio/daprd:1.13.0", "3501 (HTTP)", "service:accounting-app", "Sidecar for Microservice 2: Shares network with accounting-app. Forwards received calls to localhost:8082.")
    ]

    r_idx = 6
    for item in docker_containers:
        ws4.row_dimensions[r_idx].height = 24
        is_zebra = (r_idx % 2 == 1)
        row_fill = fill_zebra if is_zebra else fill_white

        c1 = ws4.cell(r_idx, 1, item[0])
        c1.font = font_body_bold
        c1.alignment = Alignment(horizontal="center", vertical="center")
        c1.border = thin_border
        c1.fill = row_fill

        c2 = ws4.cell(r_idx, 2, item[1])
        c2.font = font_body_bold
        c2.alignment = Alignment(horizontal="left", vertical="center")
        c2.border = thin_border
        c2.fill = row_fill

        c3 = ws4.cell(r_idx, 3, item[2])
        c3.font = font_body
        c3.alignment = Alignment(horizontal="center", vertical="center")
        c3.border = thin_border
        c3.fill = row_fill

        c4 = ws4.cell(r_idx, 4, item[3])
        c4.font = font_body
        c4.alignment = Alignment(horizontal="center", vertical="center")
        c4.border = thin_border
        c4.fill = row_fill

        c5 = ws4.cell(r_idx, 5, item[4])
        c5.font = font_body_muted
        c5.alignment = Alignment(horizontal="center", vertical="center")
        c5.border = thin_border
        c5.fill = row_fill

        ws4.merge_cells(start_row=r_idx, start_column=6, end_row=r_idx, end_column=7)
        c6 = ws4.cell(r_idx, 6, item[5])
        c6.font = font_body
        c6.alignment = Alignment(horizontal="left", vertical="center")
        c6.border = thin_border
        c6.fill = row_fill
        ws4.cell(r_idx, 7).border = thin_border
        ws4.cell(r_idx, 7).fill = row_fill
        r_idx += 1

    # Part 2: Communication Evolution (Direct HTTP vs Dapr)
    r_idx += 1
    ws4.merge_cells(f"A{r_idx}:G{r_idx}")
    ws4[f"A{r_idx}"].value = "2. COMMUNICATION EVOLUTION: STEP 1 (DIRECT HTTP) vs. STEP 2 (DAPR UPGRADE)"
    ws4[f"A{r_idx}"].font = font_sec_hdr
    ws4[f"A{r_idx}"].fill = fill_sec_hdr
    ws4[f"A{r_idx}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws4.row_dimensions[r_idx].height = 24
    r_idx += 1

    comm_comparisons = [
        ("Step 1: Direct HTTP (Starting Baseline)", "Transaction Service called 'http://accounting-app:8082/api/v1/accounting/withdraw' directly via RestTemplate. We did this FIRST to test the business logic, JSON models, and database balance deduction without any extra runtime dependencies."),
        ("Drawback of Direct HTTP", "Tight coupling: Transaction Service had to hardcode the exact hostname and port (accounting-app:8082). If the service moves, port changes, or network changes, code must be updated and recompiled."),
        ("Step 2: Dapr Service Invocation (Upgrade)", "Once direct HTTP worked, we switched to Dapr. Transaction Service calls 'http://localhost:3500/v1.0/invoke/accounting-service/method/...'. The local Dapr sidecar queries placement and forwards the call across the network to accounting-dapr, which delivers it locally to port 8082."),
        ("Key Benefit of Dapr", "Zero hardcoded URLs or ports! The caller only knows the logical app-id ('accounting-service'). Dapr automatically provides service discovery, automatic retries, and distributed tracing across containers.")
    ]

    for title, desc in comm_comparisons:
        ws4.row_dimensions[r_idx].height = 28
        c1 = ws4.cell(r_idx, 1, title)
        c1.font = font_body_bold
        c1.fill = fill_zebra
        c1.border = thin_border
        c1.alignment = Alignment(horizontal="left", vertical="center", indent=1)

        ws4.merge_cells(start_row=r_idx, start_column=2, end_row=r_idx, end_column=7)
        c2 = ws4.cell(r_idx, 2, desc)
        c2.font = font_body
        c2.border = thin_border
        c2.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        for c in range(2, 8):
            ws4.cell(r_idx, c).border = thin_border
            ws4.cell(r_idx, c).fill = fill_white
        r_idx += 1

    # Part 3: Concurrency Test Matrix
    r_idx += 1
    ws4.merge_cells(f"A{r_idx}:G{r_idx}")
    ws4[f"A{r_idx}"].value = "3. CONCURRENCY LOAD & SAFETY TEST SCENARIOS (EASY TO RUN & VERIFY)"
    ws4[f"A{r_idx}"].font = font_sec_hdr
    ws4[f"A{r_idx}"].fill = fill_sec_hdr
    ws4[f"A{r_idx}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws4.row_dimensions[r_idx].height = 24
    r_idx += 1

    test_headers = ["Scenario ID", "Test Scenario", "Initial Balance", "Withdrawal Request", "Expected Outcome", "Final Balance", "Validation Rule"]
    ws4.row_dimensions[r_idx].height = 24
    for c_i, h in enumerate(test_headers, 1):
        c = ws4.cell(r_idx, c_i, h)
        c.font = font_tbl_hdr
        c.fill = fill_tbl_hdr
        c.border = thin_border
        c.alignment = Alignment(horizontal="center", vertical="center")
    r_idx += 1

    test_cases = [
        ("TC-01", "Single User Normal Withdrawal", "₹5,000.00", "1 request for ₹500.00", "HTTP 200 OK (SUCCESS)", "₹4,500.00", "Balance reduced by exactly ₹500, transaction logged"),
        ("TC-02", "Duplicate Request Check (Idempotency)", "₹4,500.00", "Send exact same requestId twice", "1st: HTTP 200, 2nd: Cached HTTP 200", "₹4,500.00", "Second request returns saved result; NO double deduction"),
        ("TC-03", "Insufficient Balance (Overdraft)", "₹4,500.00", "1 request for ₹10,000.00", "HTTP 200 FAILED (INSUFFICIENT_BALANCE)", "₹4,500.00", "Balance untouched, friendly error 'Insufficient balance'"),
        ("TC-04", "Non-Existent Account ID", "N/A", "1 request for ACC999", "HTTP 200 FAILED (ACCOUNT_NOT_FOUND)", "N/A", "Clean error response, no database locks left open"),
        ("TC-05", "Concurrent Withdrawal Safety Test", "₹5,000.00", "2 simultaneous requests for ₹3,000", "1x SUCCESS, 1x FAILED", "₹2,000.00", "Balance NEVER drops below zero; exactly one succeeds")
    ]

    for tc in test_cases:
        ws4.row_dimensions[r_idx].height = 24
        is_zebra = (r_idx % 2 == 1)
        row_fill = fill_zebra if is_zebra else fill_white

        for c_i, v in enumerate(tc, 1):
            c = ws4.cell(r_idx, c_i, v)
            c.border = thin_border
            c.fill = row_fill
            if c_i in (1, 3, 6):
                c.alignment = Alignment(horizontal="center", vertical="center")
                c.font = font_body_bold
            elif c_i in (2, 4, 5, 7):
                c.alignment = Alignment(horizontal="left", vertical="center")
                c.font = font_body
        r_idx += 1

    ws4.column_dimensions['A'].width = 16
    ws4.column_dimensions['B'].width = 32
    ws4.column_dimensions['C'].width = 16
    ws4.column_dimensions['D'].width = 30
    ws4.column_dimensions['E'].width = 34
    ws4.column_dimensions['F'].width = 16
    ws4.column_dimensions['G'].width = 44

    wb.save("timesheet.xlsx")
    print("timesheet.xlsx successfully updated with date-based schedule and simple descriptions!")

if __name__ == "__main__":
    build_timesheet()
