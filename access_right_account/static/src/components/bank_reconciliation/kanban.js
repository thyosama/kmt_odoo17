/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { BankRecKanbanController } from "@account_accountant/components/bank_reconciliation/kanban";
import { onWillStart, useState } from "@odoo/owl";

patch(BankRecKanbanController.prototype, {
    async setup() {
        super.setup();
        this.userHasGroup = useState({
            hasAccess : false
        });
        onWillStart(async () => {
            this.orm.call("res.users", "has_group", ["access_right_account.validate_account"]).then(result => {
                this.userHasGroup.hasAccess= Boolean(result);
            })
        });
    },
    checkUserAccess() {
        return this.userHasGroup.hasAccess;
    },
});
