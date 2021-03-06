# ERPNext - web based ERP (http://erpnext.com)
# Copyright (C) 2012 Web Notes Technologies Pvt Ltd
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import webnotes 

def execute(filters=None):
	columns = get_columns()
	proj_details = get_project_details()
	pr_item_map = get_purchased_items_cost()
	se_item_map = get_issued_items_cost()
	dn_item_map = get_delivered_items_cost()

	data = []
	for project in proj_details:
		data.append([project.name, pr_item_map.get(project.name, 0), 
			se_item_map.get(project.name, 0), dn_item_map.get(project.name, 0), 
			project.project_name, project.status, project.company, 
			project.customer, project.project_value, project.project_start_date, 
			project.completion_date])

	return columns, data 

def get_columns():
	return ["Project Id:Link/Project:140", "Cost of Purchased Items:Currency:160",
		"Cost of Issued Items:Currency:160", "Cost of Delivered Items:Currency:160", 
		"Project Name::120", "Project Status::120", "Company:Link/Company:100", 
		"Customer:Link/Customer:140", "Project Value:Currency:120", 
		"Project Start Date:Date:120", "Completion Date:Date:120"]

def get_project_details():
	return webnotes.conn.sql(""" select name, project_name, status, company, customer, project_value,
		project_start_date, completion_date from tabProject where docstatus < 2""", as_dict=1)

def get_purchased_items_cost():
	pr_items = webnotes.conn.sql("""select project_name, sum(amount) as amount
		from `tabPurchase Receipt Item` where ifnull(project_name, '') != '' 
		and docstatus = 1 group by project_name""", as_dict=1)

	pr_item_map = {}
	for item in pr_items:
		pr_item_map.setdefault(item.project_name, item.amount)

	return pr_item_map

def get_issued_items_cost():
	se_items = webnotes.conn.sql("""select se.project_name, sum(se_item.amount) as amount
		from `tabStock Entry` se, `tabStock Entry Detail` se_item
		where se.name = se_item.parent and se.docstatus = 1 and ifnull(se_item.t_warehouse, '') = '' 
		and ifnull(se.project_name, '') != '' group by se.project_name""", as_dict=1)

	se_item_map = {}
	for item in se_items:
		se_item_map.setdefault(item.project_name, item.amount)

	return se_item_map

def get_delivered_items_cost():
	dn_items = webnotes.conn.sql("""select dn.project_name, sum(dn_item.amount) as amount
		from `tabDelivery Note` dn, `tabDelivery Note Item` dn_item
		where dn.name = dn_item.parent and dn.docstatus = 1 and ifnull(dn.project_name, '') != ''
		group by dn.project_name""", as_dict=1)

	si_items = webnotes.conn.sql("""select si.project_name, sum(si_item.amount) as amount
		from `tabSales Invoice` si, `tabSales Invoice Item` si_item
		where si.name = si_item.parent and si.docstatus = 1 and ifnull(si.update_stock, 0) = 1 
		and ifnull(si.is_pos, 0) = 1 and ifnull(si.project_name, '') != ''
		group by si.project_name""", as_dict=1)


	dn_item_map = {}
	for item in dn_items:
		dn_item_map.setdefault(item.project_name, item.amount)

	for item in si_items:
		dn_item_map.setdefault(item.project_name, item.amount)

	return dn_item_map