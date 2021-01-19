Feature: Milestones problems
  Check milestones problems

  Scenario: Active milestone overdue
    Given There is active milestone with due date at 2 days ago

    When Check milestone problems

    Then Problem due date overdue should be returned

  Scenario: Closed milestone overdue
    Given There is closed milestone with due date at 2 days ago

    When Check milestone problems

    Then No problems
