import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout,
    QHBoxLayout, QVBoxLayout, QGroupBox, QScrollArea, QComboBox, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt

class TaxCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("收入计算器")
        self.resize(1000, 600)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        # 左侧滚动输入区
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(20)

        # 基本信息
        base_group = QGroupBox("基本信息")
        base_layout = QGridLayout()
        base_layout.setHorizontalSpacing(15)
        base_layout.setVerticalSpacing(8)
        self.entry_salary = self.add_label_entry(base_layout, "月工资（元）", 0, "3000")
        self.entry_first_month_salary = self.add_label_entry(base_layout, "首月工资（元）", 1, "3000")
        self.entry_threshold = self.add_label_entry(base_layout, "起征点（元）", 2, "5000")
        self.entry_start_month = self.add_label_entry(base_layout, "起始月（1-12）", 3, "1")
        self.entry_end_month = self.add_label_entry(base_layout, "结束月（1-12）", 4, "12")
        self.entry_signon = self.add_label_entry(base_layout, "签字费（元）", 5, "0")
        self.entry_signon_month = self.add_label_entry(base_layout, "签字费月份", 6, "-1")
        self.entry_bonus = self.add_label_entry(base_layout, "年终奖（元）", 7, "0")
        base_group.setLayout(base_layout)

        # 五险一金比例
        rate_group = QGroupBox("五险一金缴费比例（%）【个人缴纳】")
        rate_layout = QGridLayout()
        rate_layout.setHorizontalSpacing(15)
        rate_layout.setVerticalSpacing(8)
        self.entry_pension = self.add_label_entry(rate_layout, "养老保险", 0, "8")
        self.entry_medical = self.add_label_entry(rate_layout, "医疗保险", 1, "2")
        self.entry_unemployment = self.add_label_entry(rate_layout, "失业保险", 2, "0.2")
        self.entry_fund = self.add_label_entry(rate_layout, "住房公积金", 3, "10")
        rate_group.setLayout(rate_layout)

        # 缴费基数上下限
        limit_group = QGroupBox("缴费基数上下限（元）")
        limit_layout = QGridLayout()
        limit_layout.setHorizontalSpacing(15)
        limit_layout.setVerticalSpacing(8)
        self.entry_pension_lower = self.add_label_entry(limit_layout, "养老下限", 0, "4492")
        self.entry_pension_upper = self.add_label_entry(limit_layout, "养老上限", 1, "27501")
        self.entry_medical_lower = self.add_label_entry(limit_layout, "医疗下限", 2, "6733")
        self.entry_medical_upper = self.add_label_entry(limit_layout, "医疗上限", 3, "33666")
        self.entry_unemp_lower = self.add_label_entry(limit_layout, "失业下限", 4, "2520")
        self.entry_unemp_upper = self.add_label_entry(limit_layout, "失业上限", 5, "44265")
        self.entry_fund_lower = self.add_label_entry(limit_layout, "公积金下限", 6, "2520")
        self.entry_fund_upper = self.add_label_entry(limit_layout, "公积金上限", 7, "44265")
        limit_group.setLayout(limit_layout)

        # 专项附加扣除
        extra_group = QGroupBox("专项附加扣除（元/月）")
        extra_layout = QGridLayout()
        extra_layout.setHorizontalSpacing(15)
        extra_layout.setVerticalSpacing(8)
        self.entry_edu = self.add_label_entry(extra_layout, "子女教育", 0, "0")
        self.entry_infant = self.add_label_entry(extra_layout, "婴幼儿照护", 1, "0")
        self.entry_loan = self.add_label_entry(extra_layout, "住房贷款利息", 2, "0")
        self.entry_rent = self.add_label_entry(extra_layout, "住房租金", 3, "1500")
        self.entry_elder = self.add_label_entry(extra_layout, "赡养老人", 4, "0")
        self.entry_illness = self.add_label_entry(extra_layout, "大病医疗（年）", 5, "0")
        self.entry_education_continue = self.add_label_entry(extra_layout, "继续教育（年）", 6, "0")
        self.deduction_mode = QComboBox()
        self.deduction_mode.addItems(["按月", "按年"])
        extra_layout.addWidget(QLabel("专项扣除方式"), 7, 0)
        extra_layout.addWidget(self.deduction_mode, 7, 1)
        extra_group.setLayout(extra_layout)

        # 添加所有分组到输入布局
        input_layout.addWidget(base_group)
        input_layout.addWidget(rate_group)
        input_layout.addWidget(limit_group)
        input_layout.addWidget(extra_group)

        # 计算按钮
        self.calc_button = QPushButton("计算")
        self.calc_button.setFixedHeight(40)
        input_layout.addWidget(self.calc_button)
        input_layout.addStretch(1)

        scroll_area.setWidget(input_container)
        main_layout.addWidget(scroll_area, 3)

        # 右侧结果表格
        self.output_table = QTableWidget()
        self.output_table.setColumnCount(6)
        self.output_table.setHorizontalHeaderLabels(
            ["月份", "到手工资", "个税", "医保个账", "养老金个账", "公积金账户"]
        )
        self.output_table.verticalHeader().setVisible(False)
        self.output_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.output_table.horizontalHeader().setVisible(False)
        main_layout.addWidget(self.output_table, 5)

        self.calc_button.clicked.connect(self.calculate_net_salary)

    @staticmethod
    def add_label_entry(layout, label_text, row, default_value=""):
        label = QLabel(label_text)
        entry = QLineEdit()
        entry.setText(default_value)
        layout.addWidget(label, row, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(entry, row, 1)
        return entry

    @staticmethod
    def adjust_base(base, lower, upper):
        return min(max(base, lower), upper)

    @staticmethod
    def calculate_tax(taxable):
        brackets = [
            (36000, 0.03, 0),
            (144000, 0.10, 2520),
            (300000, 0.20, 16920),
            (420000, 0.25, 31920),
            (660000, 0.30, 52920),
            (960000, 0.35, 85920),
            (float('inf'), 0.45, 181920)
        ]
        tax = 0
        if taxable > 0:
            for limit, rate, deduction in brackets:
                if taxable <= limit:
                    tax = taxable * rate - deduction
                    break
        return tax

    @staticmethod
    def calculate_bonus_tax(bonus):
        brackets = [
            (3000, 0.03, 0),
            (12000, 0.10, 210),
            (25000, 0.20, 1410),
            (35000, 0.25, 2660),
            (55000, 0.30, 4410),
            (80000, 0.35, 7160),
            (float('inf'), 0.45, 15160)
        ]
        avg = bonus / 12
        for limit, rate, deduction in brackets:
            if avg <= limit:
                tax = bonus * rate - deduction
                return max(tax, 0)
        return 0

    def calculate_net_salary(self):
        try:
            self.output_table.setRowCount(0)
            self.output_table.horizontalHeader().setVisible(True)

            def insert_item(row, col, text, bold=False):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if bold:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                self.output_table.setItem(row, col, item)

            # 表头加粗
            for col in range(self.output_table.columnCount()):
                item = self.output_table.horizontalHeaderItem(col)
                if item:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

            # 基本信息
            salary = float(self.entry_salary.text())
            first_salary = float(self.entry_first_month_salary.text())
            threshold = float(self.entry_threshold.text())
            start_month = int(self.entry_start_month.text())
            end_month = int(self.entry_end_month.text())
            months = end_month - start_month + 1
            signon = float(self.entry_signon.text())
            signon_month = int(self.entry_signon_month.text())
            bonus = float(self.entry_bonus.text())

            # 五险一金比例
            pension_rate = float(self.entry_pension.text()) / 100
            medical_rate = float(self.entry_medical.text()) / 100
            unemployment_rate = float(self.entry_unemployment.text()) / 100
            fund_rate = float(self.entry_fund.text()) / 100

            # 五险一金上下限
            pension_lower, pension_upper = float(self.entry_pension_lower.text()), float(self.entry_pension_upper.text())
            medical_lower, medical_upper = float(self.entry_medical_lower.text()), float(self.entry_medical_upper.text())
            unemp_lower, unemp_upper = float(self.entry_unemp_lower.text()), float(self.entry_unemp_upper.text())
            fund_lower, fund_upper = float(self.entry_fund_lower.text()), float(self.entry_fund_upper.text())

            # 专项附加扣除
            deduction_mode = self.deduction_mode.currentText()
            monthly_extra = sum([
                float(self.entry_edu.text()),
                float(self.entry_infant.text()),
                float(self.entry_loan.text()),
                float(self.entry_rent.text()),
                float(self.entry_elder.text())
            ])
            annual_extra = monthly_extra * months
            if deduction_mode == "按年":
                monthly_extra = 0
            illness_deduction = float(self.entry_illness.text())
            edu_continue_deduction = float(self.entry_education_continue.text())

            cumulative_income = 0
            cumulative_deduction = 0
            total_paid_tax = 0
            total_net, total_tax, total_pension, total_medical, total_unemp, total_fund = 0, 0, 0, 0, 0, 0

            # --- 月工资计算 ---
            for i in range(months):
                month = start_month + i
                month_name = f"{month}月"

                current_salary = first_salary if i == 0 else salary
                if month == signon_month:
                    current_salary += signon

                pension_base = self.adjust_base(salary, pension_lower, pension_upper)
                medical_base = self.adjust_base(salary, medical_lower, medical_upper)
                unemp_base = self.adjust_base(salary, unemp_lower, unemp_upper)
                fund_base = self.adjust_base(salary, fund_lower, fund_upper)

                pension = pension_base * pension_rate
                medical = medical_base * medical_rate
                unemp = unemp_base * unemployment_rate
                fund = fund_base * fund_rate
                insurance = pension + medical + unemp

                total_pension += pension
                total_medical += medical
                total_unemp += unemp
                total_fund += fund

                cumulative_income += current_salary
                cumulative_deduction += insurance + fund + monthly_extra + threshold

                taxable_income = cumulative_income - cumulative_deduction
                tax_all = self.calculate_tax(taxable_income)
                tax_month = tax_all - total_paid_tax
                total_paid_tax = tax_all

                net_income = current_salary - insurance - fund - tax_month
                total_net += net_income
                total_tax += tax_month

                row = self.output_table.rowCount()
                self.output_table.insertRow(row)
                for col, val in enumerate([
                    month_name,
                    f"{net_income:.2f}",
                    f"{tax_month:.2f}",
                    f"{medical:.2f}",
                    f"{pension:.2f}",
                    f"{fund * 2:.2f}"
                ]):
                    insert_item(row, col, val)

            # --- 年终奖单独计税 ---
            bonus_tax, bonus_net = 0, 0
            if bonus > 0:
                bonus_tax = self.calculate_bonus_tax(bonus)
                bonus_net = bonus - bonus_tax
                row = self.output_table.rowCount()
                self.output_table.insertRow(row)
                for col, val in enumerate([
                    "年终奖",
                    f"{bonus_net:.2f}",
                    f"{bonus_tax:.2f}",
                    "", "", ""
                ]):
                    insert_item(row, col, val, bold=True)
                total_net += bonus_net

            # --- 合计行 ---
            row = self.output_table.rowCount()
            self.output_table.insertRow(row)
            for col, val in enumerate([
                "合计",
                f"{total_net:.2f}",
                f"{total_tax + bonus_tax:.2f}",
                f"{total_medical:.2f}",
                f"{total_pension:.2f}",
                f"{total_fund * 2:.2f}"
            ]):
                insert_item(row, col, val, bold=True)

            # --- 年度退税/补税 ---
            final_total_deduction = (
                threshold * 12 +
                annual_extra +
                total_pension + total_medical + total_fund + total_unemp +
                illness_deduction + edu_continue_deduction
            )
            final_taxable = cumulative_income - final_total_deduction
            final_tax = self.calculate_tax(final_taxable)
            refund = total_tax - final_tax
            row = self.output_table.rowCount()
            self.output_table.insertRow(row)
            for col, val in enumerate([
                "年度退税",
                f"{refund:.2f}",
                "", "", "", ""
            ]):
                insert_item(row, col, val, bold=True)

        except ValueError:
            self.output_table.setRowCount(0)
            self.output_table.horizontalHeader().setVisible(False)
            self.output_table.insertRow(0)
            item = QTableWidgetItem("⚠️ 请输入有效数字！")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.output_table.setItem(0, 0, item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)

    window = TaxCalculator()
    window.show()
    sys.exit(app.exec())
