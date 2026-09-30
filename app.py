import sqlite3
from datetime import date, datetime
from contextlib import closing

import streamlit as st



DB_NAME = "todo.db"

PRIORITIES = ["High", "Medium", "Low"]
CATEGORIES = ["College", "Personal", "Work", "Other"]
STATUSES = ["Pending", "Completed"]




st.set_page_config(
    page_title="TaskFlow - Todo Manager",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded",
)




st.markdown(
    """
    <style>

    /* ---------- Main page ---------- */

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* ---------- Header ---------- */

    .app-header {
        padding: 1.5rem 0 1rem 0;
    }

    .app-title {
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0.2rem;
    }

    .app-subtitle {
        color: #6b7280;
        font-size: 1.05rem;
        margin-bottom: 1rem;
    }

    /* ---------- Metric cards ---------- */

    .metric-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 1rem 1.2rem;
        min-height: 105px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    .metric-label {
        color: #6b7280;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        margin-top: 0.2rem;
    }

    /* ---------- Task cards ---------- */

    .task-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    }

    .task-title {
        font-size: 1.15rem;
        font-weight: 750;
        margin-bottom: 0.25rem;
    }

    .task-description {
        color: #6b7280;
        font-size: 0.92rem;
        margin-bottom: 0.65rem;
    }

    .task-completed {
        text-decoration: line-through;
        color: #9ca3af;
    }

    /* ---------- Badges ---------- */

    .badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        margin-right: 0.35rem;
    }

    .priority-high {
        background: #fee2e2;
        color: #b91c1c;
    }

    .priority-medium {
        background: #fef3c7;
        color: #92400e;
    }

    .priority-low {
        background: #dcfce7;
        color: #166534;
    }

    .status-pending {
        background: #dbeafe;
        color: #1d4ed8;
    }

    .status-completed {
        background: #dcfce7;
        color: #166534;
    }

    .category-badge {
        background: #f3f4f6;
        color: #374151;
    }

    /* ---------- Empty state ---------- */

    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: #6b7280;
    }

    .empty-icon {
        font-size: 3rem;
    }

    /* ---------- Sidebar ---------- */

    section[data-testid="stSidebar"] {
        border-right: 1px solid #e5e7eb;
    }

    /* ---------- Buttons ---------- */

    .stButton > button {
        border-radius: 9px;
        font-weight: 600;
    }

    /* ---------- Divider ---------- */

    hr {
        margin: 1.2rem 0;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    """
    Create a SQLite database connection.
    """
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """
    Create the tasks table if it does not already exist.
    """

    with closing(get_connection()) as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                priority TEXT NOT NULL,
                due_date TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.commit()




def create_task(
    name,
    description,
    priority,
    due_date,
    category
):
    """
    Insert a new task.
    """

    now = datetime.now().isoformat(timespec="seconds")

    with closing(get_connection()) as connection:

        connection.execute(
            """
            INSERT INTO tasks
            (
                name,
                description,
                priority,
                due_date,
                category,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                description,
                priority,
                due_date.isoformat(),
                category,
                "Pending",
                now,
                now,
            ),
        )

        connection.commit()


def get_tasks():
    """
    Return all tasks.
    """

    with closing(get_connection()) as connection:

        rows = connection.execute(
            """
            SELECT *
            FROM tasks
            ORDER BY
                CASE WHEN status = 'Pending' THEN 0 ELSE 1 END,
                due_date ASC,
                id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_task(task_id):
    """
    Return one task by ID.
    """

    with closing(get_connection()) as connection:

        row = connection.execute(
            """
            SELECT *
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()

    return dict(row) if row else None


def update_task(
    task_id,
    name,
    description,
    priority,
    due_date,
    category
):
    """
    Update an existing task.
    """

    now = datetime.now().isoformat(timespec="seconds")

    with closing(get_connection()) as connection:

        connection.execute(
            """
            UPDATE tasks
            SET
                name = ?,
                description = ?,
                priority = ?,
                due_date = ?,
                category = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                name,
                description,
                priority,
                due_date.isoformat(),
                category,
                now,
                task_id,
            ),
        )

        connection.commit()


def toggle_task_status(task_id):
    """
    Switch Pending <-> Completed.
    """

    task = get_task(task_id)

    if not task:
        return

    new_status = (
        "Completed"
        if task["status"] == "Pending"
        else "Pending"
    )

    now = datetime.now().isoformat(timespec="seconds")

    with closing(get_connection()) as connection:

        connection.execute(
            """
            UPDATE tasks
            SET
                status = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                new_status,
                now,
                task_id,
            ),
        )

        connection.commit()


def delete_task(task_id):
    """
    Delete a task.
    """

    with closing(get_connection()) as connection:

        connection.execute(
            """
            DELETE FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        )

        connection.commit()


def clear_completed_tasks():
    """
    Delete every completed task.
    """

    with closing(get_connection()) as connection:

        connection.execute(
            """
            DELETE FROM tasks
            WHERE status = 'Completed'
            """
        )

        connection.commit()


# ============================================================
# VALIDATION
# ============================================================

def validate_task(name, description, priority, due_date, category):
    """
    Validate task input.
    """

    errors = []

    if not name.strip():
        errors.append("Task name is required.")

    if len(name.strip()) > 150:
        errors.append("Task name must be 150 characters or less.")

    if len(description.strip()) > 1000:
        errors.append(
            "Description must be 1000 characters or less."
        )

    if priority not in PRIORITIES:
        errors.append("Invalid priority.")

    if category not in CATEGORIES:
        errors.append("Invalid category.")

    if not isinstance(due_date, date):
        errors.append("Please select a valid due date.")

    return errors


def priority_icon(priority):
    icons = {
        "High": "🔴",
        "Medium": "🟡",
        "Low": "🟢",
    }

    return icons.get(priority, "⚪")


def priority_class(priority):
    return {
        "High": "priority-high",
        "Medium": "priority-medium",
        "Low": "priority-low",
    }.get(priority, "")


def format_date(date_string):
    """
    Convert YYYY-MM-DD to a readable format.
    """

    try:

        parsed = datetime.strptime(
            date_string,
            "%Y-%m-%d"
        )

        return parsed.strftime("%d %b %Y")

    except ValueError:

        return date_string


def is_overdue(task):
    """
    Determine whether a pending task is overdue.
    """

    if task["status"] == "Completed":
        return False

    try:

        due = datetime.strptime(
            task["due_date"],
            "%Y-%m-%d"
        ).date()

        return due < date.today()

    except ValueError:

        return False


# ============================================================
# FILTERING
# ============================================================

def filter_tasks(
    tasks,
    search,
    status,
    priority,
    category,
    sort_order
):
    """
    Apply search, filters and sorting.
    """

    result = tasks.copy()

    # Search
    if search.strip():

        search_value = search.strip().lower()

        result = [
            task
            for task in result
            if search_value in task["name"].lower()
        ]

    # Status
    if status != "All":

        result = [
            task
            for task in result
            if task["status"] == status
        ]

    # Priority
    if priority != "All":

        result = [
            task
            for task in result
            if task["priority"] == priority
        ]

    # Category
    if category != "All":

        result = [
            task
            for task in result
            if task["category"] == category
        ]

    # Sort
    if sort_order == "Due Date ↑":

        result.sort(
            key=lambda task: task["due_date"]
        )

    elif sort_order == "Due Date ↓":

        result.sort(
            key=lambda task: task["due_date"],
            reverse=True
        )

    elif sort_order == "Priority":

        priority_order = {
            "High": 0,
            "Medium": 1,
            "Low": 2,
        }

        result.sort(
            key=lambda task:
            priority_order.get(
                task["priority"],
                99
            )
        )

    return result




initialize_database()



st.markdown(
    """
    <div class="app-header">
        <div class="app-title">✅ TaskFlow</div>
        <div class="app-subtitle">
            A simple and powerful task manager for your everyday work.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)



with st.sidebar:

    st.markdown("## ➕ New Task")
    st.caption("Add a task to your list.")

    with st.form("create_task_form"):

        name = st.text_input(
            "Task name *",
            placeholder="e.g. Complete Python assignment",
        )

        description = st.text_area(
            "Description",
            placeholder="Optional details...",
            height=100,
        )

        priority = st.selectbox(
            "Priority",
            PRIORITIES,
            format_func=lambda value:
                f"{priority_icon(value)} {value}",
        )

        due_date = st.date_input(
            "Due date",
            value=date.today(),
        )

        category = st.selectbox(
            "Category",
            CATEGORIES,
        )

        submitted = st.form_submit_button(
            "➕ Add Task",
            use_container_width=True,
            type="primary",
        )

        if submitted:

            errors = validate_task(
                name,
                description,
                priority,
                due_date,
                category,
            )

            if errors:

                for error in errors:
                    st.error(error)

            else:

                create_task(
                    name.strip(),
                    description.strip(),
                    priority,
                    due_date,
                    category,
                )

                st.success("Task added successfully.")

                st.rerun()



tasks = get_tasks()



total_count = len(tasks)

completed_count = sum(
    task["status"] == "Completed"
    for task in tasks
)

pending_count = total_count - completed_count

overdue_count = sum(
    is_overdue(task)
    for task in tasks
)


metric1, metric2, metric3, metric4 = st.columns(4)


with metric1:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">📋 Total Tasks</div>
            <div class="metric-value">{total_count}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with metric2:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">⏳ Pending</div>
            <div class="metric-value">{pending_count}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with metric3:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">✅ Completed</div>
            <div class="metric-value">{completed_count}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with metric4:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">⚠️ Overdue</div>
            <div class="metric-value">{overdue_count}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.write("")



with st.container(border=True):

    st.markdown("### 🔎 Find Your Tasks")

    filter1, filter2, filter3 = st.columns([2, 1, 1])


    with filter1:

        search = st.text_input(
            "Search",
            placeholder="Search tasks by name...",
            label_visibility="collapsed",
        )


    with filter2:

        status_filter = st.selectbox(
            "Status",
            ["All"] + STATUSES,
            label_visibility="collapsed",
        )


    with filter3:

        priority_filter = st.selectbox(
            "Priority",
            ["All"] + PRIORITIES,
            format_func=lambda value:
                "All" if value == "All"
                else f"{priority_icon(value)} {value}",
            label_visibility="collapsed",
        )


    filter4, filter5 = st.columns(2)


    with filter4:

        category_filter = st.selectbox(
            "Category",
            ["All"] + CATEGORIES,
            label_visibility="collapsed",
        )


    with filter5:

        sort_order = st.selectbox(
            "Sort",
            [
                "Default",
                "Due Date ↑",
                "Due Date ↓",
                "Priority",
            ],
            label_visibility="collapsed",
        )



filtered_tasks = filter_tasks(
    tasks,
    search,
    status_filter,
    priority_filter,
    category_filter,
    sort_order,
)




st.markdown("### 📋 Your Tasks")

header_col1, header_col2 = st.columns([3, 1])


with header_col1:

    st.caption(
        f"Showing {len(filtered_tasks)} of {total_count} tasks"
    )


with header_col2:

    if completed_count > 0:

        if st.button(
            "🔄 Clear Completed",
            use_container_width=True,
        ):

            clear_completed_tasks()

            st.toast(
                "Completed tasks cleared!",
                icon="🧹",
            )

            st.rerun()




if not filtered_tasks:

    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-icon">📝</div>
            <h3>No tasks found</h3>
            <p>Add a new task or change your search filters.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

else:

    for task in filtered_tasks:

        task_id = task["id"]

        completed = task["status"] == "Completed"

        title_class = (
            "task-completed"
            if completed
            else ""
        )

        priority_css = priority_class(
            task["priority"]
        )

        status_css = (
            "status-completed"
            if completed
            else "status-pending"
        )

        overdue_text = ""

        if is_overdue(task):

            overdue_text = (
                '<span class="badge priority-high">'
                '⚠️ Overdue'
                '</span>'
            )


        with st.container(border=True):

            left, middle, right = st.columns(
                [0.07, 0.68, 0.25]
            )


           
            with left:

                checked = st.checkbox(
                    "Complete",
                    value=completed,
                    key=f"complete_{task_id}",
                    label_visibility="collapsed",
                )

                if checked != completed:

                    toggle_task_status(task_id)

                    st.rerun()


            

            with middle:

                st.markdown(
                    f"""
                    <div class="task-title {title_class}">
                        {task["name"]}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if task["description"]:

                    st.markdown(
                        f"""
                        <div class="task-description">
                            {task["description"]}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


                st.markdown(
                    f"""
                    <span class="badge {priority_css}">
                        {priority_icon(task["priority"])}
                        {task["priority"]}
                    </span>

                    <span class="badge category-badge">
                        📁 {task["category"]}
                    </span>

                    <span class="badge {status_css}">
                        {"✓ Completed" if completed else "⏳ Pending"}
                    </span>

                    {overdue_text}

                    <span class="badge category-badge">
                        📅 {format_date(task["due_date"])}
                    </span>
                    """,
                    unsafe_allow_html=True,
                )


           
            with right:

                edit_key = f"editing_{task_id}"

                if st.button(
                    "✏️ Edit",
                    key=f"edit_{task_id}",
                    use_container_width=True,
                ):

                    st.session_state[edit_key] = True


                if st.button(
                    "❌ Delete",
                    key=f"delete_{task_id}",
                    use_container_width=True,
                ):

                    delete_task(task_id)

                    st.toast(
                        "Task deleted.",
                        icon="🗑️",
                    )

                    st.rerun()


           

            if st.session_state.get(
                edit_key,
                False,
            ):

                st.markdown("---")
                st.markdown("#### ✏️ Edit Task")

                with st.form(
                    f"edit_form_{task_id}"
                ):

                    edit_name = st.text_input(
                        "Task name",
                        value=task["name"],
                    )

                    edit_description = st.text_area(
                        "Description",
                        value=task["description"],
                    )

                    edit_priority = st.selectbox(
                        "Priority",
                        PRIORITIES,
                        index=PRIORITIES.index(
                            task["priority"]
                        ),
                        format_func=lambda value:
                            f"{priority_icon(value)} {value}",
                    )

                    edit_due_date = st.date_input(
                        "Due date",
                        value=datetime.strptime(
                            task["due_date"],
                            "%Y-%m-%d"
                        ).date(),
                    )

                    edit_category = st.selectbox(
                        "Category",
                        CATEGORIES,
                        index=CATEGORIES.index(
                            task["category"]
                        ),
                    )

                    save_col, cancel_col = st.columns(2)


                    with save_col:

                        save = st.form_submit_button(
                            "💾 Save Changes",
                            use_container_width=True,
                            type="primary",
                        )


                    with cancel_col:

                        cancel = st.form_submit_button(
                            "Cancel",
                            use_container_width=True,
                        )


                    if save:

                        errors = validate_task(
                            edit_name,
                            edit_description,
                            edit_priority,
                            edit_due_date,
                            edit_category,
                        )

                        if errors:

                            for error in errors:
                                st.error(error)

                        else:

                            update_task(
                                task_id,
                                edit_name.strip(),
                                edit_description.strip(),
                                edit_priority,
                                edit_due_date,
                                edit_category,
                            )

                            st.session_state[
                                edit_key
                            ] = False

                            st.toast(
                                "Task updated successfully.",
                                icon="💾",
                            )

                            st.rerun()


                    if cancel:

                        st.session_state[
                            edit_key
                        ] = False

                        st.rerun()




st.divider()

st.caption(
    "TaskFlow • Built with Python, Streamlit and SQLite"
)