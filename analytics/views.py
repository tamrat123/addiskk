import os
import django
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from tracking.models import FileRecord, DailyWorkSubmission, AuditLog, Notification, SystemSetting
from accounts.models import Branch, CustomUser
import xlsxwriter
from io import BytesIO
import datetime
from django.db.models.functions import TruncDate, TruncMonth

# Reportlab imports
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.units import inch

@login_required
def dashboard(request):
    if request.user.role in ['HQ_ADMIN', 'BRANCH_MANAGER']:
        return hq_dashboard(request)
    else:
        return branch_dashboard(request)

def hq_dashboard(request):
    total_digitized = DailyWorkSubmission.objects.aggregate(Sum('files_digitized_count'))['files_digitized_count__sum'] or 0
    total_pages = DailyWorkSubmission.objects.aggregate(Sum('pages_scanned_count'))['pages_scanned_count__sum'] or 0
    today = datetime.date.today()
    today_digitized = DailyWorkSubmission.objects.filter(date=today).aggregate(Sum('files_digitized_count'))['files_digitized_count__sum'] or 0
    settings = SystemSetting.load()
    completion_rate = (total_digitized / settings.organization_target * 100) if settings.organization_target > 0 else 0
    branches_count = Branch.objects.count()
    active_branches = Branch.objects.filter(status='Active').count()
    
    branch_stats = Branch.objects.annotate(
        total_docs=Sum('dailyworksubmission__files_digitized_count'),
        today_docs=Sum('dailyworksubmission__files_digitized_count', filter=Q(dailyworksubmission__date=today)),
        today_pages=Sum('dailyworksubmission__pages_scanned_count', filter=Q(dailyworksubmission__date=today))
    )
    
    overall_today = 0
    overall_total = 0
    overall_today_pages = 0
    
    for s in branch_stats:
        s.fixed_daily_target = 400
        s.fixed_page_target = 12000
        
        s.today_docs_val = s.today_docs or 0
        s.total_docs_val = s.total_docs or 0
        s.today_pages_val = s.today_pages or 0
        
        s.today_perf = (s.today_docs_val / s.fixed_daily_target) * 100
        s.total_perf = (s.total_docs_val / s.total_target * 100) if s.total_target > 0 else 0
        s.page_perf = (s.today_pages_val / s.fixed_page_target) * 100
        
        s.remaining_files = s.total_target - s.total_docs_val
        if s.remaining_files < 0:
            s.remaining_files = 0
            
        s.expected_finish_days = s.remaining_files / s.fixed_daily_target
        
        overall_today += s.today_docs_val
        overall_total += s.total_docs_val
        overall_today_pages += s.today_pages_val

    # Branch Rank by Overall Performance
    branch_stats = list(branch_stats)
    branch_stats.sort(key=lambda x: x.total_perf, reverse=True)
    for idx, s in enumerate(branch_stats, 1):
        s.rank = idx
        
    overall_today_perf = (overall_today / 4800) * 100
    overall_total_perf = (overall_total / 69929) * 100

    from ethiopian_date import EthiopianDateConverter
    months_am = ["መስከረም", "ጥቅምት", "ህዳር", "ታህሳስ", "ጥር", "የካቲት", "መጋቢት", "ሚያዝያ", "ግንቦት", "ሰኔ", "ሐምሌ", "ነሐሴ", "ጳጉሜ"]

    # Daily Trend (Last 7 Days)
    end_date = today
    start_date = end_date - datetime.timedelta(days=6)
    daily_subs = DailyWorkSubmission.objects.filter(date__range=[start_date, end_date]) \
        .values('date') \
        .annotate(count=Sum('files_digitized_count')) \
        .order_by('date')
    trends_dict = {s['date']: s['count'] for s in daily_subs}
    daily_trends = []
    curr = start_date
    while curr <= end_date:
        try:
            eth_date = EthiopianDateConverter.to_ethiopian(curr.year, curr.month, curr.day)
            label = f"{months_am[eth_date.month-1]} {eth_date.day}"
        except:
            label = curr.strftime('%b %d')
        daily_trends.append({'label': label, 'count': trends_dict.get(curr, 0)})
        curr += datetime.timedelta(days=1)

    # Monthly Trend (Last 6 Months)
    monthly_subs = DailyWorkSubmission.objects.annotate(month=TruncMonth('date')) \
        .values('month') \
        .annotate(count=Sum('files_digitized_count')) \
        .order_by('month')[:6]
    monthly_trends = []
    for s in monthly_subs:
        m_date = s['month']
        try:
            eth_date = EthiopianDateConverter.to_ethiopian(m_date.year, m_date.month, m_date.day)
            label = months_am[eth_date.month-1]
        except:
            label = m_date.strftime('%B')
        monthly_trends.append({'label': label, 'count': s['count']})
    
    # Branch Distribution (Pie Chart Data)
    branch_dist = [{'label': b.name, 'count': b.total_docs or 0} for b in branch_stats if (b.total_docs or 0) > 0]

    audit_logs = AuditLog.objects.all().order_by('-timestamp')[:5]
    
    context = {
        'total_files': total_digitized,
        'total_pages': total_pages,
        'today_progress': today_digitized,
        'active_branches': f"{active_branches} / {branches_count}",
        'completion_rate': f"{completion_rate:.1f}%",
        'branch_stats': branch_stats,
        'audit_logs': audit_logs,
        'daily_trends': daily_trends,
        'monthly_trends': monthly_trends,
        'branch_dist': branch_dist,
        'org_target': SystemSetting.load().organization_target,
        'overall_today_perf': overall_today_perf,
        'overall_total_perf': overall_total_perf
    }
    return render(request, 'analytics/hq_dashboard.html', context)

def branch_dashboard(request):
    branch = request.user.branch
    if not branch:
        return render(request, 'analytics/error.html', {'message': 'Your account is not associated with any branch.'})
    if request.user.role == 'BRANCH_MANAGER':
        base_qs = DailyWorkSubmission.objects.filter(branch=branch)
    else:
        base_qs = DailyWorkSubmission.objects.filter(operator=request.user)

    stats = base_qs.aggregate(
        total=Sum('files_digitized_count'),
        pages=Sum('pages_scanned_count')
    )
    total_files = stats['total'] or 0
    total_pages = stats['pages'] or 0
    completion_rate = (total_files / branch.total_target * 100) if branch.total_target > 0 else 0
    recent_submissions = base_qs.order_by('-date')[:10]
    
    fixed_daily_target = 400
    remaining_files = branch.total_target - total_files
    if remaining_files < 0:
        remaining_files = 0
    expected_finish_days = remaining_files / fixed_daily_target

    all_branches = Branch.objects.annotate(
        total_docs=Sum('dailyworksubmission__files_digitized_count')
    )
    for b in all_branches:
        b.total_docs_val = b.total_docs or 0
        b.total_perf = (b.total_docs_val / b.total_target * 100) if b.total_target > 0 else 0
    
    all_branches = sorted(all_branches, key=lambda x: x.total_perf, reverse=True)
    branch_rank = next((idx for idx, b in enumerate(all_branches, 1) if b.id == branch.id), "-")
    
    from ethiopian_date import EthiopianDateConverter
    months_am = ["መስከረም", "ጥቅምት", "ህዳር", "ታህሳስ", "ጥር", "የካቲት", "መጋቢት", "ሚያዝያ", "ግንቦት", "ሰኔ", "ሐምሌ", "ነሐሴ", "ጳጉሜ"]

    # Branch-specific daily trend
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=6)
    daily_subs = base_qs.filter(date__range=[start_date, today]) \
        .values('date') \
        .annotate(count=Sum('files_digitized_count')) \
        .order_by('date')
    trends_dict = {s['date']: s['count'] for s in daily_subs}
    daily_trends = []
    curr = start_date
    while curr <= today:
        try:
            eth_date = EthiopianDateConverter.to_ethiopian(curr.year, curr.month, curr.day)
            label = f"{months_am[eth_date.month-1]} {eth_date.day}"
        except:
            label = curr.strftime('%b %d')
        daily_trends.append({'label': label, 'count': trends_dict.get(curr, 0)})
        curr += datetime.timedelta(days=1)

    context = {
        'branch': branch,
        'total_files': total_files,
        'total_pages': total_pages,
        'completion_rate': f"{completion_rate:.1f}%",
        'recent_submissions': recent_submissions,
        'daily_trends': daily_trends,
        'remaining_files': remaining_files,
        'expected_finish_days': expected_finish_days,
        'branch_rank': branch_rank,
    }
    return render(request, 'analytics/branch_dashboard.html', context)

@login_required
def branch_list_view(request):
    if request.user.role not in ['HQ_ADMIN', 'BRANCH_MANAGER']:
        return redirect('dashboard')
    branches = Branch.objects.annotate(
        total_files=Sum('dailyworksubmission__files_digitized_count'),
        total_pages=Sum('dailyworksubmission__pages_scanned_count'),
        operator_count=Count('users', filter=Q(users__role='OPERATOR'))
    )
    return render(request, 'analytics/branch_list.html', {'branches': branches})

@login_required
@login_required
def reports_view(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    start_date_obj = None
    end_date_obj = None
    days = 1
    if start_date and end_date:
        try:
            start_date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            days = (end_date_obj - start_date_obj).days + 1
            if days < 1: days = 1
        except ValueError:
            pass
    elif start_date:
        try:
            start_date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError: pass
    elif end_date:
        try:
            end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError: pass

    if request.user.role in ['HQ_ADMIN', 'BRANCH_MANAGER']:
        q_filter = Q()
        if start_date:
            q_filter &= Q(dailyworksubmission__date__gte=start_date)
        if end_date:
            q_filter &= Q(dailyworksubmission__date__lte=end_date)
            
        stats = Branch.objects.annotate(
            total=Sum('dailyworksubmission__files_digitized_count', filter=q_filter),
            pages=Sum('dailyworksubmission__pages_scanned_count', filter=q_filter)
        )
        
        overall_total_files = 0
        overall_total_pages = 0
        overall_total_target = 0
        
        for s in stats:
            s.total_val = s.total or 0
            s.pages_val = s.pages or 0
            s.daily_avg = s.total_val / days
            s.period_target = 400 * days
            s.performance = (s.total_val / s.period_target * 100) if s.period_target > 0 else 0
            
            overall_total_files += s.total_val
            overall_total_pages += s.pages_val
            overall_total_target += s.period_target
            
        overall_performance = (overall_total_files / overall_total_target * 100) if overall_total_target > 0 else 0

        # Detailed submissions list for HQ
        submissions_q = DailyWorkSubmission.objects.all()
        if start_date:
            submissions_q = submissions_q.filter(date__gte=start_date)
        if end_date:
            submissions_q = submissions_q.filter(date__lte=end_date)
        submissions = submissions_q.order_by('-date')

        return render(request, 'analytics/reports.html', {
            'stats': stats,
            'submissions': submissions,
            'is_hq': True,
            'start_date': start_date,
            'end_date': end_date,
            'start_date_obj': start_date_obj,
            'end_date_obj': end_date_obj,
            'days': days,
            'overall': {
                'files': overall_total_files,
                'pages': overall_total_pages,
                'performance': overall_performance,
                'target': overall_total_target,
                'org_target': SystemSetting.load().organization_target
            }
        })
    else:
        branch = request.user.branch
        if request.user.role == 'BRANCH_MANAGER':
            submissions = DailyWorkSubmission.objects.filter(branch=branch)
        else:
            submissions = DailyWorkSubmission.objects.filter(operator=request.user)
            
        if start_date:
            submissions = submissions.filter(date__gte=start_date)
        if end_date:
            submissions = submissions.filter(date__lte=end_date)
            
        submissions = submissions.order_by('-date')
        
        total_files = submissions.aggregate(Sum('files_digitized_count'))['files_digitized_count__sum'] or 0
        total_pages = submissions.aggregate(Sum('pages_scanned_count'))['pages_scanned_count__sum'] or 0
        period_target = 400 * days
        performance = (total_files / period_target * 100) if period_target > 0 else 0

        return render(request, 'analytics/reports.html', {
            'submissions': submissions, 
            'is_hq': False, 
            'branch': branch,
            'start_date': start_date,
            'end_date': end_date,
            'start_date_obj': start_date_obj,
            'end_date_obj': end_date_obj,
            'summary': {
                'files': total_files,
                'pages': total_pages,
                'performance': performance,
                'target': period_target,
                'days': days
            }
        })

@login_required
def export_excel(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date == 'None' or not start_date: start_date = None
    if end_date == 'None' or not end_date: end_date = None
    
    q_filter = Q()
    if start_date:
        q_filter &= Q(dailyworksubmission__date__gte=start_date)
    if end_date:
        q_filter &= Q(dailyworksubmission__date__lte=end_date)

    # Filter by branch if not HQ Admin
    branches = Branch.objects.all()
    if request.user.role != 'HQ_ADMIN':
        return HttpResponse("Unauthorized", status=403)

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Branch Statistics')
    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#4F46E5', 'font_color': 'white'})
    headers = ['የቅርንጫፍ ስም', 'ዲጂታይዝ የተደረጉ', 'ስካን የተደረጉ ገጾች', 'የቀን ግብ', 'ጠቅላላ ግብ']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_fmt)
    
    branch_stats = branches.annotate(
        total_files=Sum('dailyworksubmission__files_digitized_count', filter=q_filter),
        total_pages=Sum('dailyworksubmission__pages_scanned_count', filter=q_filter)
    )
    for row, stat in enumerate(branch_stats, start=1):
        worksheet.write(row, 0, stat.name)
        worksheet.write(row, 1, stat.total_files or 0)
        worksheet.write(row, 2, stat.total_pages or 0)
        worksheet.write(row, 3, stat.daily_target)
        worksheet.write(row, 4, stat.total_target)
    
    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=branch_statistics.xlsx'
    return response

@login_required
def export_pdf(request):
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # Register Amharic-compatible font
    # Look for bundled font first (for Production), then fallback to Windows local path
    bundled_font = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'AbyssinicaSIL-Regular.ttf')
    windows_font = r"C:\Windows\Fonts\nyala.ttf"
    
    if os.path.exists(bundled_font):
        pdfmetrics.registerFont(TTFont('AmharicFont', bundled_font))
        main_font = 'AmharicFont'
    elif os.path.exists(windows_font):
        pdfmetrics.registerFont(TTFont('AmharicFont', windows_font))
        main_font = 'AmharicFont'
    else:
        main_font = 'Helvetica'

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date == 'None' or not start_date: start_date = None
    if end_date == 'None' or not end_date: end_date = None
    
    q_filter = Q()
    if start_date:
        q_filter &= Q(dailyworksubmission__date__gte=start_date)
    if end_date:
        q_filter &= Q(dailyworksubmission__date__lte=end_date)

    if request.user.role != 'HQ_ADMIN':
        return HttpResponse("Unauthorized", status=403)
    
    branches = Branch.objects.all()
    report_title = "ጠቅላላ የቅርንጫፍ አፈፃፀም ሪፖርት"

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Add Logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.jpg')
    if os.path.exists(logo_path):
        img = Image(logo_path, 1.2*inch, 0.4*inch)
        img.hAlign = 'LEFT'
        elements.append(img)
    
    # Organization Name
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=main_font,
        fontSize=16,
        spaceAfter=6,
        textColor=colors.HexColor("#4F46E5")
    )
    elements.append(Paragraph("የአዲስ ከተማ ክፍለ ከተማ የሲቪል ምዝገባና የነዋሪነት አገልግሎት ጽ/ቤት", title_style))
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontName=main_font,
        fontSize=14,
        spaceAfter=12
    )
    elements.append(Paragraph(report_title, subtitle_style))
    
    # Period
    normal_am_style = ParagraphStyle('NormalAm', parent=styles['Normal'], fontName=main_font)
    period_text = f"የሪፖርት ጊዜ: {start_date or 'ከመጀመሪያ'} እስከ {end_date or 'ዛሬ'}"
    elements.append(Paragraph(period_text, normal_am_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Section 1: Branch Summary
    summary_header = ParagraphStyle('SummaryHeader', parent=subtitle_style, spaceBefore=12)
    elements.append(Paragraph("የቅርንጫፎች አጠቃላይ አፈፃፀም ማጠቃለያ", summary_header))
    
    data = [['የቅርንጫፍ ስም', 'ዲጂታይዝ የተደረጉ', 'ስካን የተደረጉ ገጾች', 'የቀን ግብ', 'ጠቅላላ ግብ']]
    branch_stats = branches.annotate(
        total_files=Sum('dailyworksubmission__files_digitized_count', filter=q_filter),
        total_pages=Sum('dailyworksubmission__pages_scanned_count', filter=q_filter)
    )
    
    for stat in branch_stats:
        data.append([
            stat.name,
            str(stat.total_files or 0),
            str(stat.total_pages or 0),
            str(stat.daily_target),
            str(stat.total_target)
        ])
    
    table = Table(data, hAlign='LEFT', colWidths=[2.2*inch, 1.4*inch, 1.4*inch, 0.9*inch, 0.9*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), main_font),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.4*inch))

    # Section 2: Detailed Daily Submissions
    detailed_header = ParagraphStyle('DetailedHeader', parent=subtitle_style)
    elements.append(Paragraph("ዝርዝር የዕለት ተዕለት የሥራ አፈፃፀም", detailed_header))
    
    # Fetch submissions
    from analytics.templatetags.ethiopian_calendar import to_ethiopian
    submissions_q = DailyWorkSubmission.objects.filter(branch__in=branches)
    if start_date:
        submissions_q = submissions_q.filter(date__gte=start_date)
    if end_date:
        submissions_q = submissions_q.filter(date__lte=end_date)
    submissions = submissions_q.order_by('-date')

    sub_data = [['ቀን (ኢትዮጵያ)', 'ቅርንጫፍ', 'ፋይሎች', 'ገጾች', 'ኦፕሬተር']]
    for sub in submissions:
        sub_data.append([
            to_ethiopian(sub.date),
            sub.branch.name,
            str(sub.files_digitized_count),
            str(sub.pages_scanned_count),
            sub.operator.username
        ])
    
    sub_table = Table(sub_data, hAlign='LEFT', colWidths=[1.2*inch, 1.5*inch, 1*inch, 1*inch, 2.1*inch])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#10B981")), # Green header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), main_font),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(sub_table)
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(f"የተዘጋጀበት ቀን: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_am_style))
    
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontName=main_font)
    elements.append(Paragraph(f"ያረጋገጠው: {request.user.get_full_name() or request.user.username}", footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"{report_title.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response

@login_required
def audit_logs_view(request):
    if request.user.role != 'HQ_ADMIN':
        return redirect('dashboard')
    logs = AuditLog.objects.all().order_by('-timestamp')
    return render(request, 'analytics/audit_logs.html', {'logs': logs})

@login_required
def admin_panel_view(request):
    if request.user.role != 'HQ_ADMIN':
        return redirect('dashboard')
    branches = Branch.objects.all().annotate(operator_count=Count('users'))
    users = CustomUser.objects.all()
    settings = SystemSetting.load()
    if request.method == 'POST' and 'save_settings' in request.POST:
        settings.organization_target = request.POST.get('org_target', 50000)
        settings.backup_frequency = request.POST.get('backup_freq', 'Daily')
        settings.alert_threshold_days = request.POST.get('alert_threshold', 2)
        settings.save()
        return redirect('admin_panel')
    return render(request, 'analytics/admin_panel.html', {'branches': branches, 'users': users, 'settings': settings})