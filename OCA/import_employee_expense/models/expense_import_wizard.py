# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import xlrd, csv, base64
from datetime import datetime


class Import_Wizard(models.TransientModel):
    _name = 'expense.import.wizard'

    file = fields.Binary(string="Document")

    filename = fields.Char(string="Document Name", invisible=1)

    filetype = fields.Selection([['xls', 'XLS'], ['csv', 'CSV']], string="Document Type")

    import_type = fields.Selection([['expense', 'Expense'], ['sheet', 'Expense Sheet']],
                                   string="Import", default='expense')

    product_by = fields.Selection([['name', 'Name'], ['default_code', 'Internal Reference'], ['barcode', 'Barcode']],
                                  string="Product By", default='name')

    employee_by = fields.Selection([['name', 'Name'], ['work_phone', 'Work Phone'], ['work_email', 'Work Email']],
                                   string="Employee By", default='name')

    sample_option = fields.Selection([('csv', 'CSV'), ('xls', 'XLS')], string='Sample Type', default='csv')
    down_samp_file = fields.Boolean(string='Download Sample Files')

    def import_file(self):
        expense = []
        if (self.filetype == "xls"):
            try:
                data = base64.b64decode(self.file)

                with open('/tmp/' + self.filename, 'wb') as file:
                    file.write(data)
                workbook = xlrd.open_workbook(file.name)
                sheet_names = workbook.sheet_names()
                sheet = workbook.sheet_by_name(sheet_names[0])
            except Exception:
                raise ValidationError(_("You have selected invalid file"))

            rows = sheet.nrows
            cols = sheet.ncols

            for i in range(1, rows):
                temp = []
                for j in range(0, cols):
                    temp.append(sheet.cell_value(i, j))
                expense.append(temp)

        elif (self.filetype == "csv"):
            rows = []
            try:
                data = base64.b64decode(self.file)

                with open('/tmp/' + self.filename, 'wb') as file:
                    file.write(data)
                with open(file.name, "r") as csvfile:
                    csvreader = csv.reader(csvfile)
                    for row in csvreader:
                        rows.append(row)
            except Exception:
                raise ValidationError(_("You have selected invalid file"))

            for row in rows:
                t = []
                for col in row:
                    t.append(col)
                expense.append(t)
            del expense[0]

        else:
            raise ValidationError(_('Select a File Type'))

        if self.import_type == 'expense':
            self.create_expense(expense)
        else:
            self.create_expenses_sheet(expense)
        return

    def create_expense(self, expense):
        expense_id = False
        total_expense = 0
        expense_ids = []
        for exp in expense:
            if expense:
                if self.product_by == 'name':
                    if not exp[2]:
                        raise ValidationError(_('Name for Product cannot be empty.'))

                    product = self.env['product.product'].search([['name', 'like', exp[2]]], limit=1)
                elif self.product_by == 'barcode':
                    if not exp[3]:
                        raise ValidationError(_('Barcode for Product cannot be empty.'))

                    product = self.env['product.product'].search([['barcode', 'like', exp[3]]], limit=1)
                elif self.product_by == 'default_code':
                    if not exp[4]:
                        raise ValidationError(_('Internal Reference for Product cannot be empty.'))

                    product = self.env['product.product'].search([['default_code', 'like', exp[4]]], limit=1)

                if not product:
                    raise ValidationError(_('Wrong Product Search Paramter for Product %s' % exp[2]))

                if self.employee_by == 'name':
                    if not exp[7]:
                        raise ValidationError(_('Name for Employee cannot be empty.'))

                    employee = self.env['hr.employee'].search([['name', 'like', exp[7]]], limit=1)
                elif self.employee_by == 'work_email':
                    if not exp[8]:
                        raise ValidationError(_('Work Email for Employee cannot be empty.'))

                    employee = self.env['hr.employee'].search([['work_email', 'like', exp[8]]], limit=1)
                elif self.employee_by == 'work_phone':
                    if not exp[9]:
                        raise ValidationError(_('Work Phone for Employee cannot be empty.'))

                    employee = self.env['hr.employee'].search([['work_phone', 'like', exp[9]]], limit=1)

                if not employee:
                    raise ValidationError(_('Wrong Employee Search Paramter for Employee %s' % exp[7]))

                account = self.env['account.analytic.account'].search([['name', 'like', exp[10]]], limit=1)
                saleorder = self.env['sale.order'].search([('name', 'like', exp[14])], limit=1)

                try:
                    date = '-'.join(exp[11].split('/'))
                    datetime.strptime(date, "%Y-%m-%d").strftime('%Y-%m-%d')
                except Exception:
                    raise ValidationError(_('Wrong Date Format %s. Date Should be in format YYYY/MM/DD' % exp[11]))

                if exp[12] == "Employee":
                    payment = 'own_account'
                elif exp[12] == "Company":
                    payment = 'company_account'
                else:
                    raise ValidationError(_('Should be Paid By Employee or Company'))

                if exp[5]:
                    total_expense = int(exp[6]) * int(exp[5])

                expense_id = self.env['hr.expense'].create({
                    'name': exp[1],
                    'product_id': product.id,
                    'product_uom_id': product.uom_id.id,
                    'price_unit': exp[5],
                    'quantity': exp[6],
                    'employee_id': employee.id,
                    'expense_name': exp[0],
                    'date': date,
                    'payment_mode': payment,
                    'sale_order_id': saleorder.id,
                    'total_amount': total_expense,
                })
                if expense_id:
                    expense_ids.append(expense_id.id)

            else:
                raise ValidationError(_('Empty File'))

        return expense_ids

    def create_expenses_sheet(self, expense):
        get_ids = self.create_expense(expense)
        expense_ids = self.env['hr.expense'].search([('id', 'in', get_ids)])
        emp_exp = expense_ids.mapped('employee_id')
        for record in emp_exp:
            expense_ids_set = expense_ids.filtered(lambda l: l.employee_id == record)
            dict = []
            exp_name = []

            for rec in expense_ids_set:
                if rec.expense_name:
                    exp_name.append(rec.expense_name)
                dict.append(rec.id)

            if len(set(exp_name)) == 1:
                self.env['hr.expense.sheet'].create({
                        'name': exp_name[0],
                        'employee_id': record.id,
                        'expense_line_ids': dict,
                    }
                    )
            else:
                for ans in expense_ids_set:
                    self.env['hr.expense.sheet'].create({
                        'name': ans.expense_name,
                        'employee_id': record.id,
                        'expense_line_ids': ans,
                    })

    def download_auto(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=expense.import.wizard&id=%s' % (self.id),
            'target': 'new',
        }


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    expense_name = fields.Char('Expenses Name')
