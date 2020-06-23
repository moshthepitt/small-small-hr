# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestEmails::test_leave_emails 1'] = '''Mosh Pitt requested time off:

5 days of Regular Leave
Mon, 05 Jun 2017 - Sat, 10 Jun 2017
Available Balance: 17.00 days

Please log in to process the above: http://example.com/reviews/1338

Thank you,


example.com
------
http://example.com
'''

snapshots['TestEmails::test_leave_emails 2'] = 'Mosh Pitt requested time off:<br /><br />5 days of Regular Leave<br />Mon, 05 Jun 2017 - Sat, 10 Jun 2017<br />Available Balance: 17.00 days<br /><br />Please log in to process the above: http://example.com/reviews/1338<br/><br/>Thank you,<br/>example.com<br/>------<br/>http://example.com'

snapshots['TestEmails::test_overtime_emails 1'] = '''Mosh Pitt requested overtime:

4 hours 45 minutes on Mon, 05 Jun 2017
4:45 p.m. - 9:30 p.m.

Please log in to process the above: http://example.com/reviews/1337

Thank you,


example.com
------
http://example.com
'''

snapshots['TestEmails::test_overtime_emails 2'] = 'Mosh Pitt requested overtime:<br /><br />4 hours 45 minutes on Mon, 05 Jun 2017<br />4:45 p.m. - 9:30 p.m.<br /><br />Please log in to process the above: http://example.com/reviews/1337<br/><br/>Thank you,<br/>example.com<br/>------<br/>http://example.com'

snapshots['TestEmails::test_leave_emails 3'] = '''Mosh Pitt,

Your time off request for 5 days of Regular Leave from 05 Jun - 10 Jun has been approved.

Mon, 05 Jun 2017 - Sat, 10 Jun 2017
Regular Leave
5 days
Status: Approved

Thank you,


example.com
------
http://example.com
'''

snapshots['TestEmails::test_leave_emails 4'] = 'Mosh Pitt,<br /><br />Your time off request for 5 days of Regular Leave from 05 Jun - 10 Jun has been approved.<br /><br />Mon, 05 Jun 2017 - Sat, 10 Jun 2017<br />Regular Leave<br />5 days<br />Status: Approved<br/><br/>Thank you,<br/>example.com<br/>------<br/>http://example.com'

snapshots['TestEmails::test_leave_emails 5'] = '''Mosh Pitt,

Your time off request for 5 days of Regular Leave from 05 Jun - 10 Jun has been rejected.

Mon, 05 Jun 2017 - Sat, 10 Jun 2017
Regular Leave
5 days
Status: Rejected

Thank you,


example.com
------
http://example.com
'''

snapshots['TestEmails::test_leave_emails 6'] = 'Mosh Pitt,<br /><br />Your time off request for 5 days of Regular Leave from 05 Jun - 10 Jun has been rejected.<br /><br />Mon, 05 Jun 2017 - Sat, 10 Jun 2017<br />Regular Leave<br />5 days<br />Status: Rejected<br/><br/>Thank you,<br/>example.com<br/>------<br/>http://example.com'

snapshots['TestEmails::test_overtime_emails 3'] = '''Mosh Pitt,

Your overtime request for 4 hours 45 minutes has been approved.

4 hours 45 minutes on Mon, 05 Jun 2017
4:45 p.m. - 9:30 p.m.
Status: Approved

Thank you,

example.com
------
http://example.com
'''

snapshots['TestEmails::test_overtime_emails 4'] = 'Mosh Pitt,<br /><br />Your overtime request for 4 hours 45 minutes has been approved.<br /><br />4 hours 45 minutes on Mon, 05 Jun 2017<br />4:45 p.m. - 9:30 p.m.<br />Status: ApprovedThank you,<br/>example.com<br/>------<br/>http://example.com'

snapshots['TestEmails::test_overtime_emails 5'] = '''Mosh Pitt,

Your overtime request for 4 hours 45 minutes has been rejected.

4 hours 45 minutes on Mon, 05 Jun 2017
4:45 p.m. - 9:30 p.m.
Status: Rejected

Thank you,

example.com
------
http://example.com
'''

snapshots['TestEmails::test_overtime_emails 6'] = 'Mosh Pitt,<br /><br />Your overtime request for 4 hours 45 minutes has been rejected.<br /><br />4 hours 45 minutes on Mon, 05 Jun 2017<br />4:45 p.m. - 9:30 p.m.<br />Status: RejectedThank you,<br/>example.com<br/>------<br/>http://example.com'
