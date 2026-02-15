"""填充业务数据库示例数据（200+ 条）"""
import random
from datetime import date, timedelta
from pathlib import Path

from app.database.connection import get_engine
from app.database.models import BusinessBase, Department, Employee, Product, SalesRecord


def _random_date(start: date, end: date) -> date:
    d = (end - start).days
    return start + timedelta(days=random.randint(0, d) if d > 0 else 0)


def run_seed():
    """创建表并填充数据"""
    engine = get_engine()
    BusinessBase.metadata.create_all(bind=engine)

    from sqlalchemy.orm import Session

    dept_names = ["技术部", "销售部", "市场部", "人事部", "财务部", "运营部"]
    managers = ["张伟", "李娜", "王强", "刘洋", "陈静", "杨帆"]
    positions = ["工程师", "经理", "专员", "主管", "总监", "助理"]
    categories = ["电子产品", "办公用品", "生活用品", "食品", "服装"]

    with Session(engine) as session:
        if session.query(Department).first():
            print("已有数据，跳过 seed")
            return

        depts = []
        for i, (name, mgr) in enumerate(zip(dept_names, managers)):
            d = Department(
                name=name,
                manager=mgr,
                budget=round(random.uniform(50, 500) * 10000, 2),
            )
            session.add(d)
            depts.append(d)
        session.commit()
        session.refresh(depts[-1])
        dept_ids = [d.id for d in depts]

        employees = []
        for _ in range(60):
            e = Employee(
                name=random.choice(["张", "李", "王", "刘", "陈", "杨", "赵", "黄"]) + random.choice("伟强芳敏静磊娜洋"),
                department_id=random.choice(dept_ids),
                position=random.choice(positions),
                salary=round(random.uniform(8, 50) * 1000, 2),
                hire_date=_random_date(date(2018, 1, 1), date(2024, 6, 1)),
            )
            session.add(e)
            employees.append(e)
        session.commit()
        for e in employees:
            session.refresh(e)
        emp_ids = [e.id for e in employees]

        products = []
        for i in range(40):
            p = Product(
                name=f"{random.choice(categories)}-{i+1}",
                category=random.choice(categories),
                price=round(random.uniform(10, 2000), 2),
                stock=random.randint(0, 500),
            )
            session.add(p)
            products.append(p)
        session.commit()
        for p in products:
            session.refresh(p)
        prod_ids = [p.id for p in products]

        for _ in range(220):
            p_id = random.choice(prod_ids)
            e_id = random.choice(emp_ids)
            qty = random.randint(1, 20)
            # 从 session 取 price 简化处理：用随机单价
            unit_price = round(random.uniform(20, 1500), 2)
            r = SalesRecord(
                product_id=p_id,
                employee_id=e_id,
                quantity=qty,
                amount=round(qty * unit_price, 2),
                sale_date=_random_date(date(2024, 1, 1), date(2025, 2, 14)),
            )
            session.add(r)
        session.commit()

    print("Seed 完成：departments, employees, products, sales_records 已填充 200+ 条")


if __name__ == "__main__":
    run_seed()
