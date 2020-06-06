# small-small-hr

[![Build Status](https://travis-ci.org/moshthepitt/small-small-hr.svg?branch=master)](https://travis-ci.org/moshthepitt/small-small-hr)

`small-small-hr` is a really really small and light-weight Django application that helps you (yes you!) to manage certain aspects of HR (human resource) in your small or large business/organization/whatever.

## Installation

```sh
pip install small-small-hr
```

## Features

At this time, `small-small-hr` supports the following:

### Employee records

You can keep track of all your employee's details.  This is achieved through a custom `StaffProfile` model attached to your `User` model via a `one-to-one` relationship.  Some of the available fields on this model are:

* first name
* last name
* gender
* birth day
* photo
* number of allowed leave days per year
* whether or not overtime is allowed for the employee
* data - a JSON field that allows you to store any extra information

### Employee Documents

You can keep track of an unlimited number of employee documents (think employment contracts, performance reviews, scans of identification documents, etc).  This is achieved by an `StaffDocument` model that has a `one-to-many` relationship with the `StaffProfile` model (above).

The fields on this model are

* staffprofile_id
* name of document
* description of document
* dcoument file

### Leave management

All employees can log in and make a request for leave.  To achieve this, there exists a `LeaveRequest` model with these fields:

* staffprofile_id
* request date
* start date
* end date
* reason for leave
* status (pending approval/approved/rejected)
* comments (made by the admin, e.g. reasons for refusal)

Once a LeaveRequest object is created, an administrator should review it and approve/reject it.

### Overtime hours tracking

Employees who are allowed overtime can log in and record overtime hours.  This is done by an `OvertimeHour` model with these fields:

* staffprofile_id
* date
* start time
* end time
* reason for overtime
* status (pending approval/approved/rejected)
* comments (made by the admin, e.g. reasons for refusal)

Admins can download overtime hours reports for a particular period.

## Contribution

All contributions are welcome.

To set up the project:

1. Clone this repo
2. `pip install -r requirements/dev.txt`
3. `pre-commit install`

## Testing

```sh

pip install -U tox

tox
```
