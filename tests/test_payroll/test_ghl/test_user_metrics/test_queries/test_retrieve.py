GHL_USER_METRICS = """
{
  me {
    id
    name
    glAvatar
    roles
    hourRate
    taxRate
    annualPaidWorkBreaksDays
    position {
      title
    }
    metrics {
      lastSalaryDate
      paidWorkBreaksDays
      bonus
      penalty
      issues {
        openedCount
        openedSpent
        closedSpent
        payrollClosed
        payrollOpened
        payroll
        taxesClosed
        taxesOpened
        taxes
      }
      mergeRequests {
        openedCount
        openedSpent
        closedSpent
        payrollClosed
        payrollOpened
        payroll
        taxesClosed
        taxesOpened
        taxes
      }
      openedSpent
      closedSpent
      payrollClosed
      payrollOpened
      payroll
      taxesClosed
      taxesOpened
      taxes
    }
  }
}
"""


def test_query(user, ghl_client):
    """
    Test query.

    :param user:
    :param ghl_client:
    """
    ghl_client.set_user(user)

    response = ghl_client.execute(GHL_USER_METRICS)

    assert "errors" not in response
