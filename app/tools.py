import json
from langchain_core.tools import tool
from app.database import get_db_connection

@tool
def log_personal_expense(description: str, amount: float, category: str) -> str:
    """
    Logs a solo personal expense into PostgreSQL.
    Categories: Food, Transport, Utilities, Entertainment, Shopping, Health, Other.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO personal_expenses (description, amount, category)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (description, amount, category.capitalize())
            )
            expense_id = cursor.fetchone()["id"]
            conn.commit()
    return f"Logged expense #{expense_id}: '{description}' of ${amount:.2f} under [{category.capitalize()}]."

@tool
def split_group_bill(title: str, total_amount: float, payer: str, debts_json: str) -> str:
    """
    Records a group outing bill and tracks individual debts (IOUs).
    'debts_json' MUST be a valid JSON string mapping names to amounts owed.
    Example: '{"Alex": 35.0, "Ben": 35.0, "Sarah": 50.0}'
    """
    try:
        debts = json.loads(debts_json)
    except Exception as e:
        return f"Error parsing debts_json format: {str(e)}"

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # Insert master outing bill
            cursor.execute(
                """
                INSERT INTO group_bills (title, total_amount, payer)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (title, total_amount, payer)
            )
            bill_id = cursor.fetchone()["id"]

            # Insert each individual debtor
            breakdown = []
            for debtor, owed in debts.items():
                cursor.execute(
                    """
                    INSERT INTO iou_records (bill_id, debtor_name, amount_owed)
                    VALUES (%s, %s, %s);
                    """,
                    (bill_id, debtor, float(owed))
                )
                breakdown.append(f"{debtor}: ${float(owed):.2f}")
            conn.commit()

    return f"Group bill '{title}' (${total_amount:.2f}) recorded. Breakdown of debts: {', '.join(breakdown)}."

@tool
def get_pending_ious() -> str:
    """
    Fetches all unsettled IOUs to show who owes money.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT i.id, g.title, i.debtor_name, i.amount_owed, g.created_at
                FROM iou_records i
                JOIN group_bills g ON i.bill_id = g.id
                WHERE i.is_settled = FALSE
                ORDER BY g.created_at DESC;
            """)
            rows = cursor.fetchall()

    if not rows:
        return "All IOUs are settled! Nobody owes you money."

    total_uncollected = sum(float(r["amount_owed"]) for r in rows)
    lines = [f"- {r['debtor_name']} owes ${float(r['amount_owed']):.2f} for '{r['title']}'" for r in rows]
    return f"Pending IOUs (Total Outstanding: ${total_uncollected:.2f}):\n" + "\n".join(lines)

@tool
def query_expense_summary(category: str = None) -> str:
    """
    Summarizes personal expenses, optionally filtered by category.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            if category:
                cursor.execute(
                    "SELECT description, amount FROM personal_expenses WHERE LOWER(category) = LOWER(%s);",
                    (category,)
                )
            else:
                cursor.execute("SELECT description, amount, category FROM personal_expenses;")
            rows = cursor.fetchall()

    if not rows:
        return f"No expenses found{' in ' + category.capitalize() if category else ''}."

    total = sum(float(r["amount"]) for r in rows)
    return f"Total spending{' in ' + category.capitalize() if category else ''}: ${total:.2f} across {len(rows)} entries."

@tool
def settle_debt(debtor_name: str) -> str:
    """
    Marks all pending IOUs as settled (paid) for a specific person.
    Use this when the user says someone paid them back or settled their debt.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            # Update the database to mark debts as true for this person
            cursor.execute(
                """
                UPDATE iou_records 
                SET is_settled = TRUE 
                WHERE LOWER(debtor_name) = LOWER(%s) AND is_settled = FALSE;
                """,
                (debtor_name,)
            )
            updated_rows = cursor.rowcount
            conn.commit()

    if updated_rows == 0:
        return f"No pending debts found for {debtor_name}."
    
    return f"Successfully settled {updated_rows} pending debt(s) for {debtor_name}."

finance_tools = [
    log_personal_expense,
    split_group_bill,
    get_pending_ious,
    query_expense_summary,
    settle_debt
]