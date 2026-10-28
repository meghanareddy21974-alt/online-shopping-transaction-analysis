from database import get_db


def _where(start, end, extra=""):
    clauses, params = [], []
    if start:
        clauses.append("order_date >= ?"); params.append(start)
    if end:
        clauses.append("order_date <= ?"); params.append(end)
    if extra:
        clauses.append(extra)
    return ("WHERE " + " AND ".join(clauses)) if clauses else "", params


def _rows(db, sql, params):
    return [dict(r) for r in db.execute(sql, params)]


def build_report(start=None, end=None):
    db = get_db()
    w_all, p_all = _where(start, end)
    w_ok, p_ok = _where(start, end, "status='Delivered'")

    k = db.execute(f"SELECT COUNT(*) orders, COUNT(DISTINCT customer_id) customers, "
                   f"COALESCE(SUM(total),0) revenue FROM transactions {w_ok}", p_ok).fetchone()
    orders, revenue = k["orders"], round(k["revenue"], 2)

    repeat = db.execute(f"SELECT COUNT(*) c FROM (SELECT customer_id FROM transactions {w_ok} "
                        f"GROUP BY customer_id HAVING COUNT(*) > 1)", p_ok).fetchone()["c"]

    status = _rows(db, f"SELECT status, COUNT(*) count FROM transactions {w_all} GROUP BY status", p_all)
    total_orders = sum(s["count"] for s in status)
    returned = next((s["count"] for s in status if s["status"] == "Returned"), 0)
    cancelled = next((s["count"] for s in status if s["status"] == "Cancelled"), 0)

    return {
        "kpis": {
            "revenue": revenue,
            "orders": orders,
            "customers": k["customers"],
            "avg_order_value": round(revenue / orders, 2) if orders else 0,
            "repeat_rate": round(repeat / k["customers"] * 100, 1) if k["customers"] else 0,
            "return_rate": round(returned / total_orders * 100, 1) if total_orders else 0,
            "cancel_rate": round(cancelled / total_orders * 100, 1) if total_orders else 0,
        },
        "monthly": _rows(db, f"SELECT substr(order_date,1,7) month, ROUND(SUM(total),2) revenue, "
                             f"COUNT(*) orders FROM transactions {w_ok} GROUP BY month ORDER BY month", p_ok),
        "categories": _rows(db, f"SELECT category, ROUND(SUM(total),2) revenue FROM transactions {w_ok} "
                                f"GROUP BY category ORDER BY revenue DESC", p_ok),
        "payments": _rows(db, f"SELECT payment_method, COUNT(*) count FROM transactions {w_ok} "
                              f"GROUP BY payment_method ORDER BY count DESC", p_ok),
        "status": status,
        "top_products": _rows(db, f"SELECT product, SUM(quantity) units, ROUND(SUM(total),2) revenue "
                                  f"FROM transactions {w_ok} GROUP BY product ORDER BY revenue DESC LIMIT 10", p_ok),
        "top_customers": _rows(db, f"SELECT customer_id, COUNT(*) orders, ROUND(SUM(total),2) spent "
                                   f"FROM transactions {w_ok} GROUP BY customer_id ORDER BY spent DESC LIMIT 10", p_ok),
    }
