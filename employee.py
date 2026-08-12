import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="WFH Dashboard",
    layout="wide"
)

st.title("Weekly Attendance Dashboard")

# Allow user to upload a CSV/Excel file
uploaded_file = st.file_uploader("Upload attendance CSV or Excel", type=["csv", "xlsx", "xls"])
if uploaded_file is None:
    st.info("Upload a CSV or Excel attendance file to load the dashboard.")
    st.stop()

try:
    if uploaded_file.name.lower().endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.success(f"Loaded {uploaded_file.name}")
except Exception as e:
    st.error(f"Failed to read uploaded file: {e}")
    st.stop()

df.columns = df.columns.astype(str).str.strip()
if df.columns.duplicated().any():
    counts = {}
    new_columns = []
    for col in df.columns:
        if col in counts:
            counts[col] += 1
            new_columns.append(f"{col}.{counts[col]}")
        else:
            counts[col] = 0
            new_columns.append(col)
    df.columns = new_columns
    st.warning("Duplicate column names were found and renamed for uniqueness. Please verify your selected columns.")

# Candidate column names for the key fields
EMPLOYEE_CANDIDATES = ["DTS-RESOURCE", "Employee", "Employee Name", "Resource", "Name"]
DATE_CANDIDATES = ["Date", "DATE", "date", "Attendance Date", "AttendanceDate", "Work Date", "Day"]
LOCATION_CANDIDATES = ["Location", "LOCATION", "Work Location", "Office/Location", "Workplace"]
EMPID_CANDIDATES = ["EMPID", "Emp ID", "Employee ID", "ID"]
ATTENDANCE_CANDIDATES = ["ATTENDANCE", "Attendance", "ATTEND"]
SEAT_CANDIDATES = ["SEAT-INFO", "Seat-Info", "SEAT INFO", "SEAT_INFO", "SEAT"]


def find_column(columns, candidates):
    normalized = {col.strip().lower(): col for col in columns}
    for candidate in candidates:
        if candidate in columns:
            return candidate
        lower = candidate.strip().lower()
        if lower in normalized:
            return normalized[lower]
    return None

all_cols = df.columns.tolist()

EMPLOYEE_DEFAULT = find_column(all_cols, EMPLOYEE_CANDIDATES)
DATE_DEFAULT = find_column(all_cols, DATE_CANDIDATES)
LOCATION_DEFAULT = find_column(all_cols, LOCATION_CANDIDATES)
EMPID_DEFAULT = find_column(all_cols, EMPID_CANDIDATES)
ATTENDANCE_DEFAULT = find_column(all_cols, ATTENDANCE_CANDIDATES)
SEAT_DEFAULT = find_column(all_cols, SEAT_CANDIDATES)

EMPLOYEE_COLUMN = EMPLOYEE_DEFAULT
DATE_COLUMN = DATE_DEFAULT
LOCATION_COLUMN = LOCATION_DEFAULT
EMPID_COLUMN = EMPID_DEFAULT
ATTENDANCE_COLUMN = ATTENDANCE_DEFAULT
SEAT_COLUMN = SEAT_DEFAULT

if EMPID_COLUMN not in all_cols:
    EMPID_COLUMN = None
if ATTENDANCE_COLUMN not in all_cols:
    ATTENDANCE_COLUMN = None
if SEAT_COLUMN not in all_cols:
    SEAT_COLUMN = None

if DATE_COLUMN is None or EMPLOYEE_COLUMN is None or LOCATION_COLUMN is None:
    st.error("Employee, Date and Location columns are required.")
    st.stop()

st.markdown("### Uploaded file preview")
st.dataframe(df.head(10), use_container_width=True)

st.markdown("### Dataset summary")
col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("Total records", len(df))
col_b.metric("Unique employees", df[EMPLOYEE_COLUMN].nunique())
col_c.metric("Unique columns", len(df.columns))
col_d.metric("Unique locations", df[LOCATION_COLUMN].nunique())

if ATTENDANCE_COLUMN:
    st.metric("Unique attendance statuses", df[ATTENDANCE_COLUMN].nunique())

if EMPID_COLUMN:
    st.metric("Unique employee IDs", df[EMPID_COLUMN].nunique())

# Parse and normalize dates
try:
    if pd.api.types.is_integer_dtype(df[DATE_COLUMN]) or pd.api.types.is_float_dtype(df[DATE_COLUMN]):
        try:
            df[DATE_COLUMN] = pd.to_datetime(
                df[DATE_COLUMN],
                unit='D',
                origin='1899-12-30',
                errors='coerce'
            )
        except Exception:
            df[DATE_COLUMN] = pd.to_timedelta(df[DATE_COLUMN], unit='D') + pd.Timestamp('1899-12-30')
    else:
        df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN], errors="coerce")
    df = df.dropna(subset=[DATE_COLUMN])
    df[DATE_COLUMN] = df[DATE_COLUMN].dt.normalize()
except Exception as e:
    st.error(f"Failed to parse dates from column '{DATE_COLUMN}': {e}")
    st.stop()

employees = sorted(df[EMPLOYEE_COLUMN].dropna().unique())

min_date = df[DATE_COLUMN].min().date()
max_date = df[DATE_COLUMN].max().date()
unique_date_count = df[DATE_COLUMN].dt.normalize().nunique()
selected_emp = st.selectbox(
    "Select employee",
    ["All"] + list(employees),
    index=0
)

weekend_only = st.checkbox("Show only weekend records", value=False)

view_mode = st.radio("Report type", ["Daily", "Weekly", "Monthly"], index=0, horizontal=True)

selected_month = None
if view_mode == "Monthly":
    month_options = sorted(df[DATE_COLUMN].dt.to_period("M").astype(str).unique())
    selected_month = st.selectbox("Select month", month_options)

st.caption(
    f"Dataset covers {unique_date_count} distinct dates from {min_date} to {max_date}."
)


def get_work_type(location):
    loc = str(location).upper()
    if "WFH" in loc:
        return "WFH"
    if "WFO" in loc or "OFFICE" in loc:
        return "Office"
    if "ETV" in loc:
        return "ETV"
    if "EC" in loc:
        return "EC"
    return location


def add_wfh_column(df_to_update):
    result = df_to_update.copy()
    result["WFH"] = result[LOCATION_COLUMN].apply(lambda loc: get_work_type(loc) == "WFH")
    result["WORK_TYPE"] = result[LOCATION_COLUMN].apply(get_work_type)
    return result


def filter_for_weekend(df_to_filter):
    if not weekend_only:
        return df_to_filter
    return df_to_filter[df_to_filter[DATE_COLUMN].dt.weekday >= 5]


def show_day_view():
    selected_date = st.date_input(
        "Select date",
        value=min_date,
        min_value=min_date,
        max_value=max_date,
    )
    selected_date = pd.to_datetime(selected_date).normalize()

    selected_day = df[df[DATE_COLUMN] == selected_date]
    if selected_emp != "All":
        selected_day = selected_day[selected_day[EMPLOYEE_COLUMN] == selected_emp]
    selected_day = filter_for_weekend(selected_day)

    if selected_emp != "All":
        st.markdown(f"**Selected employee:** {selected_emp}")
        if EMPID_COLUMN and EMPID_COLUMN in selected_day.columns:
            empid_values = selected_day[EMPID_COLUMN].dropna().unique()
            if len(empid_values) > 0:
                st.markdown(f"**Employee ID:** {empid_values[0]}")

    st.subheader("Attendance on " + selected_date.strftime("%Y-%m-%d"))

    if selected_day.empty:
        st.warning("No attendance data found for the selected filters.")
        return

    selected_day = add_wfh_column(selected_day)

    show_cols = []
    if EMPID_COLUMN:
        show_cols.append(EMPID_COLUMN)
    show_cols.append(EMPLOYEE_COLUMN)
    if ATTENDANCE_COLUMN:
        show_cols.append(ATTENDANCE_COLUMN)
    show_cols.append(DATE_COLUMN)
    show_cols.append(LOCATION_COLUMN)
    if SEAT_COLUMN:
        show_cols.append(SEAT_COLUMN)
    show_cols.extend(["WORK_TYPE", "WFH"])
    show_cols = list(dict.fromkeys(show_cols))

    wfh_data = selected_day[selected_day["WORK_TYPE"] == "WFH"]
    office_data = selected_day[selected_day["WORK_TYPE"] == "Office"]

    total_count = len(selected_day)
    wfh_count = len(wfh_data)
    office_count = len(office_data)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total records", total_count)
    col2.metric("WFH records", wfh_count)
    col3.metric("Office records", office_count)

    st.subheader("Employees working from home")
    show_wfh_cols = [c for c in show_cols if c in wfh_data.columns]
    if show_wfh_cols:
        st.dataframe(wfh_data[show_wfh_cols].sort_values([EMPLOYEE_COLUMN]), use_container_width=True)
    else:
        st.dataframe(wfh_data.sort_values([EMPLOYEE_COLUMN]), use_container_width=True)

    st.subheader("All attendance records")
    filtered_df = selected_day[[c for c in show_cols if c in selected_day.columns]].sort_values([EMPLOYEE_COLUMN])
    st.dataframe(filtered_df, use_container_width=True)

    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download daily report",
        data=csv,
        file_name=f"daily_report_{selected_date.strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )


def render_week_table(start_week_date):
    # start_week_date is a pandas.Timestamp normalized
    week_start = start_week_date
    week_end = week_start + pd.Timedelta(days=6)
    week_df = df[(df[DATE_COLUMN] >= week_start) & (df[DATE_COLUMN] <= week_end)]
    if selected_emp != 'All':
        week_df = week_df[week_df[EMPLOYEE_COLUMN] == selected_emp]
    week_df = filter_for_weekend(week_df)
    week_df = add_wfh_column(week_df)

    if week_df.empty:
        st.warning("No attendance records found for that week.")
        return

    show_cols = []
    if EMPID_COLUMN:
        show_cols.append(EMPID_COLUMN)
    show_cols.append(EMPLOYEE_COLUMN)
    if ATTENDANCE_COLUMN:
        show_cols.append(ATTENDANCE_COLUMN)
    show_cols.append(DATE_COLUMN)
    show_cols.append(LOCATION_COLUMN)
    if SEAT_COLUMN:
        show_cols.append(SEAT_COLUMN)
    show_cols.extend(["WORK_TYPE", "WFH"])
    show_cols = list(dict.fromkeys(show_cols))

    st.subheader("Weekly attendance summary")
    st.dataframe(week_df[[c for c in show_cols if c in week_df.columns]].sort_values([DATE_COLUMN, EMPLOYEE_COLUMN]), use_container_width=True)

    csv = week_df[[c for c in show_cols if c in week_df.columns]].sort_values([DATE_COLUMN, EMPLOYEE_COLUMN]).to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download weekly report",
        data=csv,
        file_name=f"weekly_report_{week_start.strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )


if view_mode == 'Daily':
    show_day_view()
elif view_mode == 'Weekly':
    pick_date = st.date_input('Select any date in week', value=min_date, min_value=min_date, max_value=max_date)
    pick_date = pd.to_datetime(pick_date).normalize()
    start_week = pick_date - pd.Timedelta(days=pick_date.weekday())
    st.subheader(f'Week starting {start_week.date().isoformat()}')
    render_week_table(start_week)
else:
    selected_month_period = pd.Period(selected_month, freq='M')
    month_df = df[df[DATE_COLUMN].dt.to_period('M') == selected_month_period]
    if selected_emp != 'All':
        month_df = month_df[month_df[EMPLOYEE_COLUMN] == selected_emp]
    month_df = filter_for_weekend(month_df)
    month_df = add_wfh_column(month_df)

    st.subheader(f'Monthly report for {selected_month}')
    if month_df.empty:
        st.warning('No attendance records found for that month.')
    else:
        show_cols = []
        if EMPID_COLUMN:
            show_cols.append(EMPID_COLUMN)
        show_cols.append(EMPLOYEE_COLUMN)
        if ATTENDANCE_COLUMN:
            show_cols.append(ATTENDANCE_COLUMN)
        show_cols.append(DATE_COLUMN)
        show_cols.append(LOCATION_COLUMN)
        if SEAT_COLUMN:
            show_cols.append(SEAT_COLUMN)
        show_cols.extend(['WORK_TYPE', 'WFH'])
        show_cols = list(dict.fromkeys(show_cols))

        st.dataframe(month_df[[c for c in show_cols if c in month_df.columns]].sort_values([DATE_COLUMN, EMPLOYEE_COLUMN]), use_container_width=True)

        csv = month_df[[c for c in show_cols if c in month_df.columns]].sort_values([DATE_COLUMN, EMPLOYEE_COLUMN]).to_csv(index=False).encode('utf-8')
        st.download_button(
            'Download monthly report',
            data=csv,
            file_name=f'monthly_report_{selected_month.replace("-","")}.csv',
            mime='text/csv',
        )

# Day view rendering is handled inside `show_day_view()` to avoid scope issues.
