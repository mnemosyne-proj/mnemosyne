
#Code lifted from edit_fact_dlg.py, where it was first implemented for card
#type conversion, but not needed.

        # Convert fact data if needed.
        if new_card_type != self.fact.card_type:
            if not self.fact.card_type.keys().issubset(new_card_type.keys()):
                correspondence = {}
                dlg = ConvertCardTypeFieldsDlg(self.fact.card_type,
                                               new_card_type, correspondence,
                                               self)
                status = dlg.exec_()
                if status == 0: # Reject
                    return
                print correspondence
                print new_fact_data
