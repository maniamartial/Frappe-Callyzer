frappe.ui.form.on('Number Card', {
    refresh: function(frm) {
        if (frm.doc.name === 'Call Duration') {
            frappe.call({
                method: frm.doc.method,
                callback: function(r) {
                    if (r.message && r.message.value) {
                        // Format duration manually in the frontend
                        let seconds = r.message.value;
                        let duration = frappe.utils.format_duration(seconds, false);
                        frm.set_value('value', duration);
                        frm.refresh();
                    }
                }
            });
        }
    }
});