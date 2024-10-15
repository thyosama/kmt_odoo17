from odoo.http import request, Controller, route


class TimesheetController(Controller):
    @route("/timesheet", auth="user", website=True)
    def timesheet_form(self, **kwargs):
        projects = request.env["project.project"].sudo().search([])
        tasks = request.env["project.task"].sudo().search([])
        return request.render(
            "alm_self_service.timesheet_form_template",
            {"projects": projects, "tasks": tasks},
        )

    @route(
        "/timesheet/submit", type="http", auth="user", website=True, methods=["POST"]
    )
    def timesheet_form_submit(self, **post):
        employee = request.env["hr.employee"].sudo().search(
            [("portal_user_id", "=", request.env.user.id)], limit=1
        )
        error = None

        if not employee:
            error = "Employee not found for the current user."
        elif not all(
            [
                post.get("project"),
                post.get("task"),
                post.get("date"),
                post.get("hours_spent"),
            ]
        ):
            error = "All fields except description are required."
        else:
            created_line = (
                request.env["account.analytic.line"]
                .sudo()
                .create(
                    {
                        "employee_id": employee.id,
                        "project_id": int(post.get("project")),
                        "task_id": int(post.get("task")),
                        "date": post.get("date"),
                        "unit_amount": float(post.get("hours_spent")),
                        "name": post.get("description"),
                    }
                )
            )
            if not created_line:
                error = "Failed to create timesheet entry."

        if error:
            return request.render(
                "alm_self_service.timesheet_form_template",
                {
                    "error": error,
                    "projects": request.env["project.project"].sudo().search([]),
                    "tasks": request.env["project.task"].sudo().search([]),
                },
            )
        else:
            return request.redirect("/thank-you")

    @route("/my-timesheets", auth="user", website=True)
    def my_timesheets(self, page=1, **kwargs):
        page = int(page)
        employee = request.env["hr.employee"].sudo().search(
            [("portal_user_id", "=", request.env.user.id)], limit=1
        )
        items_per_page = 40
        total_timesheets = (
            request.env["account.analytic.line"]
            .sudo()
            .search_count(
                [
                    "|",
                    ("employee_id", "=", employee.id),
                    ("employee_id.timesheet_manager_id", "=", request.env.user.id),
                ]
            )
        )
        offset = (page - 1) * items_per_page

        timesheets = request.env["account.analytic.line"].sudo().search(
            [
                "|",
                ("employee_id", "=", employee.id),
                ("employee_id.timesheet_manager_id", "=", request.env.user.id),
            ],
            offset=offset,
            limit=items_per_page,
        )

        total_pages = (total_timesheets + items_per_page - 1) // items_per_page

        return request.render(
            "alm_self_service.timesheet_list_template",
            {
                "timesheets": timesheets,
                "page": page,
                "total_pages": total_pages,
                "items_per_page": items_per_page,
            },
        )

    @route(
        "/timesheet/validate/<int:timesheet_id>", type="http", auth="user", website=True
    )
    def validate_timesheet(self, timesheet_id):
        timesheet = request.env["account.analytic.line"].sudo().browse(timesheet_id)
        if (
            timesheet
            and timesheet.employee_id.timesheet_manager_id.id == request.env.user.id
        ):
            timesheet.action_validate_timesheet()
        return request.redirect("/my-timesheets")

    @route("/get_tasks", type="json", auth="user", website=True)
    def get_tasks(self, project_id):
        tasks = (
            request.env["project.task"]
            .sudo()
            .search(
                [
                    ("allow_timesheets", "=", True),
                    ("project_id", "=", int(project_id)),
                    ("is_timeoff_task", "=", False),
                ]
            )
        )
        return [{"id": task.id, "name": task.name} for task in tasks]

    @route("/thank-you", auth="user", type="http", methods=["GET"], website=True)
    def thank_you(self, **kwargs):
        return request.render("alm_self_service.thank_you_template")



class EmployeeController(Controller):
    @route("/employees", auth="user", website=True)
    def employee_list(self, page=1, **kwargs):
        # Ensure 'page' is treated as an integer
        page = int(page)

        # Number of records per page
        items_per_page = 40

        # Calculate total number of employees
        total_employees = request.env["hr.employee"].sudo().search_count([])

        # Calculate offset and limit
        offset = (page - 1) * items_per_page
        employees = request.env["hr.employee"].sudo().search([], offset=offset, limit=items_per_page)

        # Calculate total pages
        total_pages = (total_employees + items_per_page - 1) // items_per_page

        return request.render(
            "alm_self_service.employee_list_template", {
                "employees": employees,
                "page": page,
                "total_pages": total_pages,
                "items_per_page": items_per_page
            }
        )