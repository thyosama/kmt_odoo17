# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import base64
from odoo import http, SUPERUSER_ID, _
from odoo.http import request
from datetime import datetime, timedelta, time
from odoo.exceptions import ValidationError


class CreateTimeOff(http.Controller):

    @http.route(["/SelfServices"], type="http", auth="user", website=True)
    def home_page(self):
        employee = (
            request.env["hr.employee"]
            .sudo()
            .search([("portal_user_id", "=", request.env.user.id)], limit=1)
        )
        values = {}
        values.update(
            {
                "allocation_remaining_display": employee.allocation_remaining_display,
                "allocation_display": employee.allocation_display,
                "errordata": False,
                "mess": "wwwwwwwww",
            }
        )
        return request.render("self_service_module.self_service_home_page", values)

    @http.route(["/timeoff"], type="http", auth="user", website=True)
    def timeoff(self, error=None):
        domain = [
            "|",
            ("requires_allocation", "=", "no"),
            "&",
            ("has_valid_allocation", "=", True),
            "&",
            ("max_leaves", ">", "0"),
            "|",
            ("allows_negative", "=", True),
            "&",
            ("virtual_remaining_leaves", ">", 0),
            ("allows_negative", "=", False),
        ]
        type = request.env["hr.leave.type"].sudo().search(domain)
        values = {}
        values.update({"type": type, "error": error})
        return request.render("self_service_module.online_create_timeoff_form", values)

    @http.route(
        "/timeoff/submit/", type="http", auth="public", methods=["POST"], website=True
    )
    def create_online_time_off(self, **kwargs):
        type_domain = [
            "|",
            ("requires_allocation", "=", "no"),
            "&",
            ("has_valid_allocation", "=", True),
            "&",
            ("max_leaves", ">", "0"),
            "|",
            ("allows_negative", "=", True),
            "&",
            ("virtual_remaining_leaves", ">", 0),
            ("allows_negative", "=", False),
        ]
        try:
            employee = (
                request.env["hr.employee"]
                .sudo()
                .search([("portal_user_id", "=", request.env.user.id)])
            )
            attach = False

            if kwargs.get("attachment_ids"):
                Attachment = request.env["ir.attachment"]
                file_name = kwargs.get("attachment_ids").filename
                file = kwargs.get("attachment_ids")
                attach = Attachment.sudo().create(
                    {
                        "name": file_name,
                        "type": "binary",
                        "datas": base64.b64encode(file.read()),
                        "res_model": "hr.leave",
                    }
                )

            # Check for overlapping leave requests
            date_from = datetime.strptime(kwargs["date_from"], "%Y-%m-%d")
            date_to = datetime.strptime(kwargs["date_to"], "%Y-%m-%d")
            overlapping_leaves = (
                request.env["hr.leave"]
                .sudo()
                .search(
                    [
                        ("employee_id", "=", employee.id),
                        ("state", "in", ["confirm", "validate1", "validate"]),
                        "|",
                        "&",
                        ("request_date_from", "<=", date_from),
                        ("request_date_to", ">=", date_from),
                        "&",
                        ("request_date_from", "<=", date_to),
                        ("request_date_to", ">=", date_to),
                    ]
                )
            )

            if overlapping_leaves:
                overlap_msg = _("There is an overlapping leave request.")
                return request.redirect("/timeoff?error=%s" % overlap_msg)

            time_off = (
                request.env["hr.leave"]
                .sudo()
                .create(
                    {
                        "name": kwargs.get("description", ""),
                        "holiday_status_id": int(kwargs["type_id"]),
                        "request_date_from": datetime.strptime(
                            kwargs["date_from"], "%Y-%m-%d"
                        ),
                        "date_from": datetime.strptime(kwargs["date_from"], "%Y-%m-%d"),
                        "request_date_to": datetime.strptime(
                            kwargs["date_to"], "%Y-%m-%d"
                        ),
                        "date_to": datetime.strptime(kwargs["date_to"], "%Y-%m-%d"),
                        "employee_id": employee.id,
                        "supported_attachment_ids": attach,
                        "from_website": True,
                    }
                )
            )

            if time_off:
                time_off._compute_duration()

            if attach:
                time_off.supported_attachment_ids.sudo().update({"res_id": time_off.id})

            return request.redirect("/timeoff-thank-you")

        except ValidationError as e:
            error_msg = e.args[0] if e.args else "Validation error occurred."
            return request.redirect("/timeoff?error=%s" % error_msg)


        except Exception as e:
            error_msg = str(e) if e else "An unexpected error occurred."
            return request.redirect("/timeoff?error=%s" % error_msg)

    
    @http.route("/timeoff-thank-you", auth="user", type="http", methods=["GET"], website=True)
    def thank_you(self, **kwargs):
        return request.render("self_service_module.create_time_off_success")

    
    @http.route(["/timeoff/show"], type="http", auth="user", website=True)
    def show_timeoff(self):
        employee = (
            request.env["hr.employee"]
            .sudo()
            .search([("portal_user_id", "=", request.env.user.id)])
        )
        leaves = (
            request.env["hr.leave"]
            .sudo()
            .search(
                [
                    "|",
                    ("employee_id", "=", employee.id),
                    ("employee_id.leave_manager_id", "=", request.env.user.id),
                ]
            )
        )
        values = {}
        values.update(
            {
                "leaves": leaves,
                "no_leaves": len(leaves),
            }
        )
        return request.render("self_service_module.show_leaves", values)

    @http.route(
        ["/timeoff/approve/<int:leave_id>"], type="http", auth="user", website=True
    )
    def approve_leave(self, leave_id):
        leave = request.env["hr.leave"].sudo().browse(leave_id)
        if leave and leave.state == "confirm":
            leave.action_approve()
        return request.redirect("/timeoff/show")

    @http.route(["/payslips/show"], type="http", auth="user", website=True)
    def show_payslip(self):
        employee = (
            request.env["hr.employee"]
            .sudo()
            .search([("portal_user_id", "=", request.env.user.id)])
        )
        payslips = (
            request.env["hr.payslip"]
            .sudo()
            .search([("employee_id", "=", employee.id), ("state", "!=", "draft")])
        )
        values = {}
        values.update(
            {
                "payslip": payslips,
                "no_payslip": len(payslips),
            }
        )
        return request.render("self_service_module.show_payslips", values)

    @http.route(
        ["/payslips/payslipshow/<int:id>"], type="http", auth="user", website=True
    )
    def payslip_detail(self, id, **kwargs):
        payslip = request.env["hr.payslip"].sudo().search([("id", "=", id)])
        return request.render(
            "self_service_module.show_payslip_detail", {"payslip": payslip}
        )

    @http.route("/payslips/print/<int:id>", type="http", auth="user", website=True)
    def print_payslip_details(self, id, **kwargs):
        payslip = request.env["hr.payslip"].sudo().search([("id", "=", id)])
        if payslip:
            pdf, _ = (
                request.env["ir.actions.report"]
                .sudo()
                ._render_qweb_pdf(
                    "payslip_report_customization.action_print_payslip_cust",
                    [payslip.id],
                )
            )
            pdfhttpheaders = [
                ("Content-Type", "application/pdf"),
                ("Content-Length", "%s" % len(pdf)),
            ]
            return request.make_response(pdf, headers=pdfhttpheaders)

        else:
            return request.redirect("/payslips/show")
