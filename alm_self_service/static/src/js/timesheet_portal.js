/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.DynamicTasks = publicWidget.Widget.extend({
    selector: "#project",

    events: {
        change: "_onChangeProject",
    },

    /**
     * @override
     */
    start: function () {
        this._onChangeProject(); // Trigger initial call
        return this._super.apply(this, arguments);
    },

    /**
     * Called when the project selection changes.
     *
     * @private
     */
    _onChangeProject: function () {
        var project_id = this.$el.val();
        $.ajax({
            url: "/get_tasks",
            type: "POST",
            dataType: "json",
            data: JSON.stringify({ params: { project_id: project_id } }),
            contentType: "application/json",
            success: function (tasks) {
                var task_select = $("#task");
                task_select.empty().append(
                    $("<option>", {
                        value: "",
                        text: "Select Task",
                    })
                );
                if (tasks.result) {
                    $.each(tasks.result, function (key, task) {
                        if (task.id !== null && task.id !== undefined) {
                            // Check if id is not null or undefined
                            task_select.append(
                                $("<option>", {
                                    value: task.id,
                                    text: task.name,
                                })
                            );
                        }
                    });
                }
            },
            error: function (xhr, status, error) {
                console.error(xhr.responseText);
            },
        });
    },
});
