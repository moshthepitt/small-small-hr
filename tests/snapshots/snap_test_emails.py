# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestEmails::test_leave_emails 1'] = '''Mosh Pitt requested time off:

5 days of Regular Leave.
Mon, 05 Jun 2017 - Sat, 10 Jun 2017.
Available Balance: 17.00 days

Please log in to process the above: http://example.com/reviews/1

Thank you,


example.com
------
http://example.com
'''

snapshots['TestEmails::test_leave_emails 2'] = 'Mosh Pitt requested time off:<br /><br />5 days of Regular Leave.<br />Mon, 05 Jun 2017 - Sat, 10 Jun 2017.<br />Available Balance: 17.00 days<br /><br />Please log in to process the above: http://example.com/reviews/1<br/><br/>Thank you,<br/>example.com<br/>------<br/>http://example.com'
