# Synthetic Data Generation Prompt

## Context
IT ticketing system tracking the complete lifecycle of support tickets from creation through resolution. This system captures the messy reality of IT support including escalations, reassignments, reopened tickets, and varying technician skill levels.

## Data Requirements

### Format
CSV file with the following columns:
- `event_id`: Unique identifier for each ticket event
- `timestamp`: Date and time when the event occurred (format: YYYY-MM-DD HH:MM:SS)
- `ticket_id`: Associated IT ticket number (format: TKT-[YYYYMMDD]-###)
- `activity`: The ticket lifecycle activity (see Activity Types below)
- `assigned_to`: Name of the IT technician assigned to the ticket (or "Unassigned")
- `priority`: Ticket priority (Critical, High, Medium, Low)
- `category`: Type of issue (Hardware, Software, Network, Security, Access, Performance)
- `department`: Department that submitted the ticket (Engineering, Finance, HR, Sales, Operations, IT)
- `notes`: Brief description or context for the event

### Activity Types

Tickets progress through various states with realistic workflow patterns:

#### Standard Workflow Activities
- **Ticket Created**: Initial ticket submission by end user
- **Ticket Assigned**: Ticket assigned to a technician
- **Work Started**: Technician begins actively working on the issue
- **Awaiting User Response**: Technician needs information from the user
- **User Responded**: User provides requested information
- **Awaiting Parts**: Hardware or equipment needed (hardware issues)
- **Parts Received**: Required parts arrived
- **Work Resumed**: Work continues after being blocked
- **Resolution Proposed**: Technician suggests a solution for user approval
- **Ticket Resolved**: Issue marked as resolved
- **Ticket Closed**: Ticket formally closed

#### Exception/Escalation Activities
- **Ticket Reassigned**: Moved to a different technician (skill mismatch, workload balancing)
- **Escalated to L2**: Complex issue requiring senior technician
- **Escalated to L3**: Critical issue requiring specialist or vendor support
- **Escalated to Manager**: Management intervention needed
- **De-escalated**: Returned to lower support tier
- **Ticket Reopened**: Previously closed ticket reopened due to recurring issue
- **Priority Changed**: Priority level adjusted (up or down)
- **On Hold**: Temporarily paused (awaiting approval, budget, maintenance window)
- **Hold Released**: Ticket becomes active again

### Data Characteristics

#### IT Technicians with Skill Levels

**Level 1 Support (Junior)**
- **Chris Johnson**: New hire, handles basic issues, frequent escalations
- **Sam Williams**: 6 months experience, learning quickly, occasional mistakes
- **Pat Anderson**: Solid L1, handles routine issues well

**Level 2 Support (Intermediate)**
- **Alex Martinez**: Experienced generalist, good with software and hardware
- **Jordan Lee**: Database and server specialist, less comfortable with networking
- **Taylor Chen**: Network specialist, strong with infrastructure
- **Morgan Davis**: Security focused, handles access and compliance issues

**Level 3 Support (Senior)**
- **Casey Brown**: Senior architect, handles critical escalations
- **Riley Thompson**: Vendor relationship manager, complex enterprise issues

**Management**
- **IT Manager**: Handles disputes, approvals, resource conflicts

#### Realistic Messy Scenarios

**Common Patterns:**
1. **Skill Mismatch**: L1 tech gets assigned complex issue, must escalate
2. **Workload Balancing**: Tickets reassigned when techs are overloaded
3. **False Closures**: Tickets closed prematurely, then reopened
4. **Priority Creep**: Low priority tickets escalated due to executive pressure
5. **Parts Delays**: Hardware tickets stuck waiting for equipment
6. **User Ghosting**: Tickets waiting days/weeks for user response
7. **Ping-Pong Escalations**: Tickets bounced between specialists
8. **Weekend Warriors**: Complex issues that span multiple days
9. **VIP Treatment**: Executive tickets get fast-tracked
10. **Zombie Tickets**: Old tickets suddenly reactivated

#### Priority Distribution
- **Critical** (5%): System outages, security breaches, C-level issues
- **High** (15%): Multiple users affected, business-critical applications
- **Medium** (50%): Standard issues affecting single users
- **Low** (30%): Minor inconveniences, enhancement requests

#### Category Distribution
- **Software** (30%): Application crashes, license issues, updates
- **Hardware** (20%): Equipment failures, upgrades, replacements
- **Network** (15%): Connectivity issues, VPN problems, slow performance
- **Security** (15%): Access requests, password resets, suspicious activity
- **Access** (10%): Permissions, account management
- **Performance** (10%): Slow systems, resource issues

#### Temporal Patterns
- **Events span January through March 2024**
- **Business hours**: Most activity 9 AM - 5 PM weekdays
- **After-hours**: Critical issues and escalations happen 24/7
- **Response times vary**:
  - L1 assignment: 15 min - 2 hours
  - L1 to L2 escalation: 2 - 8 hours
  - L2 to L3 escalation: 4 - 24 hours
  - Parts delivery: 1 - 5 business days
  - User response: 1 hour - 2 weeks (some never respond)
- **Resolution times**:
  - Simple tickets: 30 min - 4 hours
  - Medium complexity: 4 hours - 2 days
  - Complex tickets: 2 days - 2 weeks
  - Escalated tickets: Add 50-200% to timeline

### Ticket ID Format
- Pattern: `TKT-[YYYYMMDD]-[3-digit sequence]`
- Example: `TKT-20240115-001`
- Created date matches the ticket creation timestamp

## Use Case
This data represents realistic IT support ticket workflows where:
- Tickets move through various lifecycle states
- Real-world complications affect ticket flow
- Technician skills impact resolution times and escalation rates
- Process mining can reveal:
  - Average resolution times by category and priority
  - Escalation patterns and bottlenecks
  - Technician performance and specialization
  - Common failure points (false closures, reassignments)
  - SLA compliance and violations
  - Resource allocation inefficiencies
  - Impact of skill mismatches on cycle time
  - Ticket reopening rates and root causes
  - Workload distribution across teams
  - Effects of priority changes on flow

## Sample Output
```csv
event_id,timestamp,ticket_id,activity,assigned_to,priority,category,department,notes
1,2024-01-15 09:23:15,TKT-20240115-001,Ticket Created,Unassigned,High,Software,Engineering,Database connection timeout errors
2,2024-01-15 09:35:22,TKT-20240115-001,Ticket Assigned,Sam Williams,High,Software,Engineering,Assigned to L1 support
3,2024-01-15 10:15:30,TKT-20240115-001,Work Started,Sam Williams,High,Software,Engineering,Investigating connection strings
4,2024-01-15 11:42:18,TKT-20240115-001,Escalated to L2,Jordan Lee,High,Software,Engineering,Beyond L1 scope - database expertise needed
5,2024-01-15 12:05:45,TKT-20240115-001,Work Started,Jordan Lee,High,Software,Engineering,Checking database server logs
6,2024-01-15 14:30:22,TKT-20240115-001,Resolution Proposed,Jordan Lee,High,Software,Engineering,Connection pool exhausted - configuration change proposed
7,2024-01-15 14:55:10,TKT-20240115-001,Ticket Resolved,Jordan Lee,High,Software,Engineering,Connection pool limit increased from 50 to 200
8,2024-01-15 15:10:33,TKT-20240115-001,Ticket Closed,Jordan Lee,High,Software,Engineering,User confirmed resolution
```

## Expected Patterns in Generated Data

### Ticket Journey Examples

**Simple Ticket (Happy Path)**
1. Ticket Created
2. Ticket Assigned (L1)
3. Work Started
4. Ticket Resolved
5. Ticket Closed

**Complex Ticket with Escalation**
1. Ticket Created
2. Ticket Assigned (L1)
3. Work Started
4. Escalated to L2 (skill gap)
5. Work Started (L2)
6. Awaiting Parts
7. Parts Received
8. Work Resumed
9. Resolution Proposed
10. Ticket Resolved
11. Ticket Closed

**Problematic Ticket**
1. Ticket Created
2. Ticket Assigned (L1)
3. Work Started
4. Awaiting User Response
5. [Long delay]
6. User Responded
7. Work Resumed
8. Ticket Resolved
9. Ticket Closed
10. Ticket Reopened (issue recurred)
11. Ticket Assigned (L2)
12. Work Started
13. Escalated to L3
14. Work Started (L3)
15. Resolution Proposed
16. Ticket Resolved
17. Ticket Closed

**Reassignment Chain**
1. Ticket Created
2. Ticket Assigned (Tech A)
3. Work Started
4. Ticket Reassigned (Tech A overloaded)
5. Work Started (Tech B)
6. Escalated to L2 (wrong skillset)
7. Work Started (L2 Tech)
8. Ticket Resolved
9. Ticket Closed
