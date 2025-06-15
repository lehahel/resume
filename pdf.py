# pdf_styles.py

from reportlab.lib.colors import black, navy, darkblue, darkred, darkgreen, darkslategray, lightblue, palegreen, lightgrey, white, HexColor
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from io import BytesIO
import os

from database import Resume

# Register fonts if needed (for custom fonts)
pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
pdfmetrics.registerFont(TTFont('TimesNewRoman', 'Times New Roman.ttf'))
pdfmetrics.registerFont(TTFont('Georgia', 'Georgia.ttf'))

class PhotoSettings:
    def __init__(self, width, height, x, y, is_circular):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.is_circular = is_circular

class DecorationSettings:
    def __init__(self, draw_header_line, line_color, line_thickness, draw_section_borders, border_color, draw_background_accent, accent_color):
        self.draw_header_line = draw_header_line
        self.line_color = line_color
        self.line_thickness = line_thickness
        self.draw_section_borders = draw_section_borders
        self.border_color = border_color
        self.draw_background_accent = draw_background_accent
        self.accent_color = accent_color

class PdfStyle:
    def __init__(self, name, title_font, section_font, normal_font, title_color, text_color,
                 margin_left, margin_right, margin_top, margin_bottom, line_spacing, use_two_columns,
                 photo_config, decoration_config):
        self.name = name
        self.title_font = title_font
        self.section_font = section_font
        self.normal_font = normal_font
        self.title_color = title_color
        self.text_color = text_color
        self.margin_left = margin_left
        self.margin_right = margin_right
        self.margin_top = margin_top
        self.margin_bottom = margin_bottom
        self.line_spacing = line_spacing
        self.use_two_columns = use_two_columns
        self.photo_config = photo_config
        self.decoration_config = decoration_config

# Font definitions: (font_name, size, style)
# For style: 'B' = bold, 'I' = italic, 'BI' = bold italic, '' = regular
def font(font_name, size, style=''):
    return (font_name, size, style)

STYLES = {
    "modern": PdfStyle(
        name="Modern",
        title_font=font("Arial", 18, "B"),
        section_font=font("Arial", 14, "B"),
        normal_font=font("Arial", 12, ""),
        title_color=darkblue,
        text_color=black,
        margin_left=40,
        margin_right=40,
        margin_top=40,
        margin_bottom=40,
        line_spacing=18,
        use_two_columns=False,
        photo_config=PhotoSettings(100, 100, 40, 40, True),
        decoration_config=DecorationSettings(
            draw_header_line=True,
            line_color=darkblue,
            line_thickness=2,
            draw_section_borders=False,
            border_color=black,
            draw_background_accent=True,
            accent_color=lightgrey
        )
    ),
    "classic": PdfStyle(
        name="Classic",
        title_font=font("TimesNewRoman", 16, "B"),
        section_font=font("TimesNewRoman", 14, "B"),
        normal_font=font("TimesNewRoman", 12, ""),
        title_color=black,
        text_color=black,
        margin_left=50,
        margin_right=50,
        margin_top=50,
        margin_bottom=50,
        line_spacing=20,
        use_two_columns=False,
        photo_config=PhotoSettings(80, 80, 50, 50, False),
        decoration_config=DecorationSettings(
            draw_header_line=True,
            line_color=black,
            line_thickness=1,
            draw_section_borders=True,
            border_color=black,
            draw_background_accent=False,
            accent_color=white
        )
    ),
    "creative": PdfStyle(
        name="Creative",
        title_font=font("Arial", 20, "BI"),
        section_font=font("Arial", 14, "B"),
        normal_font=font("Arial", 11, ""),
        title_color=darkred,
        text_color=HexColor("#A9A9A9"),  # darkgray
        margin_left=30,
        margin_right=30,
        margin_top=30,
        margin_bottom=30,
        line_spacing=16,
        use_two_columns=True,
        photo_config=PhotoSettings(120, 120, 30, 30, True),
        decoration_config=DecorationSettings(
            draw_header_line=False,
            line_color=darkred,
            line_thickness=0,
            draw_section_borders=True,
            border_color=darkred,
            draw_background_accent=True,
            accent_color=HexColor("#FFB6C1")  # PalePink
        )
    ),
    "professional": PdfStyle(
        name="Professional",
        title_font=font("Arial", 18, "B"),
        section_font=font("Arial", 13, "B"),
        normal_font=font("Arial", 11, ""),
        title_color=navy,
        text_color=black,
        margin_left=45,
        margin_right=45,
        margin_top=45,
        margin_bottom=45,
        line_spacing=18,
        use_two_columns=True,
        photo_config=PhotoSettings(90, 90, 45, 45, False),
        decoration_config=DecorationSettings(
            draw_header_line=True,
            line_color=navy,
            line_thickness=1.5,
            draw_section_borders=False,
            border_color=navy,
            draw_background_accent=True,
            accent_color=lightblue
        )
    ),
    "elegant": PdfStyle(
        name="Elegant",
        title_font=font("Georgia", 19, "B"),
        section_font=font("Georgia", 14, "BI"),
        normal_font=font("Georgia", 12, ""),
        title_color=darkgreen,
        text_color=darkslategray,
        margin_left=35,
        margin_right=35,
        margin_top=35,
        margin_bottom=35,
        line_spacing=19,
        use_two_columns=False,
        photo_config=PhotoSettings(110, 110, 35, 35, True),
        decoration_config=DecorationSettings(
            draw_header_line=True,
            line_color=darkgreen,
            line_thickness=2,
            draw_section_borders=True,
            border_color=darkgreen,
            draw_background_accent=True,
            accent_color=palegreen
        )
    ),
}

def get_style(style_name: str) -> PdfStyle:
    return STYLES.get(style_name.lower(), STYLES["modern"])

def get_available_styles():
    return list(STYLES.keys())

def increment_y(c, y, height, style, line_spacing):
    y -= line_spacing
    if y < style.margin_bottom + 100:
        c.showPage()
        y = height - style.margin_top
    return y

def render_resume_pdf(resume: Resume, style_name="modern", photo_base_path="photos"):
    style = get_style(style_name)
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = style.margin_top

    # Draw background accent if configured
    if style.decoration_config.draw_background_accent:
        c.setFillColor(style.decoration_config.accent_color)
        c.rect(0, height - 100, width, 100, fill=1)
        c.setFillColor(style.text_color)  # Reset fill color back to text color

    # Фото
    if resume.photo and style.photo_config:
        try:
            photo_path = resume.photo
            if not os.path.isabs(photo_path):
                photo_path = os.path.join(photo_base_path, photo_path.lstrip("/"))
            if os.path.exists(photo_path):
                img = ImageReader(photo_path)
                photo_w = style.photo_config.width
                photo_h = style.photo_config.height
                photo_x = style.photo_config.x
                if style.decoration_config.draw_background_accent:
                    photo_y = height - 100 - photo_h // 2
                else:
                    photo_y = height - style.photo_config.y - photo_h - style.margin_top

                print(photo_y, photo_h, height)
                
                if style.photo_config.is_circular:
                    # Save graphics state
                    c.saveState()
                    
                    # Draw circular background with border
                    c.setFillColor(colors.white)
                    c.setStrokeColor(style.decoration_config.line_color)
                    c.setLineWidth(1)
                    c.circle(photo_x + photo_w/2, photo_y + photo_h/2, min(photo_w, photo_h)/2, stroke=1, fill=1)
                    
                    # Create circular clip path
                    p = c.beginPath()
                    p.circle(photo_x + photo_w/2, photo_y + photo_h/2, min(photo_w, photo_h)/2)
                    c.clipPath(p, stroke=0)
                    
                    # Draw image
                    c.drawImage(img, photo_x, photo_y, photo_w, photo_h, mask='auto')
                    
                    # Restore graphics state
                    c.restoreState()
                else:
                    # Draw rectangular background with border
                    c.setFillColor(colors.white)
                    c.setStrokeColor(style.decoration_config.line_color)
                    c.setLineWidth(1)
                    c.rect(photo_x, photo_y, photo_w, photo_h, stroke=1, fill=1)
                    
                    # Draw image
                    c.drawImage(img, photo_x, photo_y, photo_w, photo_h, mask='auto')

                # Update y position if photo extends below current y position
                y = height - photo_y + style.margin_top

                    
        except Exception as ex:
            print(f"Ошибка загрузки фото: {ex}")

    # Заголовок
    header = f"{resume.firstName} {resume.middleName or ''} {resume.lastName}"
    c.setFont(style.title_font[0], style.title_font[1])
    c.setFillColor(style.title_color)
    c.drawString(style.margin_left, height - y, header)

    y += style.line_spacing * 2

    # Draw header line if configured
    if style.decoration_config.draw_header_line:
        c.setStrokeColor(style.decoration_config.line_color)
        c.setLineWidth(style.decoration_config.line_thickness)
        c.line(style.margin_left, height - y, width - style.margin_right, height - y)
        c.setStrokeColor(style.text_color)  # Reset stroke color back to text color

    y = max(y, 100 + style.line_spacing)

    # Add padding for section borders if enabled
    border_padding = 10 if style.decoration_config.draw_section_borders else 0

    # Handle two-column layout if configured
    if style.use_two_columns:
        # Store initial y position for left column
        left_y = y
    
        # Calculate column widths and positions
        content_width = width - style.margin_left - style.margin_right
        left_column_width = content_width * 0.35
        right_column_width = content_width * 0.55
        left_column_x = style.margin_left
        right_column_x = style.margin_left + left_column_width + 20

        # Draw section border for left column if configured
        if style.decoration_config.draw_section_borders:
            c.setStrokeColor(style.decoration_config.border_color)
            c.rect(left_column_x, height - left_y - 350, left_column_width, 350)
            c.setStrokeColor(style.text_color)  # Reset stroke color
        
        # Draw contact section in left column
        c.setFont(style.section_font[0], style.section_font[1])
        c.setFillColor(style.title_color)
        c.drawString(left_column_x + border_padding, height - left_y - style.line_spacing, "Контакты")
        left_y += style.line_spacing

        # Draw phone number if available
        if resume.phoneNumber:
            c.setFont(style.normal_font[0], style.normal_font[1]) 
            c.setFillColor(style.text_color)
            c.drawString(left_column_x + border_padding, height - left_y - style.line_spacing, f"Телефон: {resume.phoneNumber}")
            left_y += style.line_spacing

        # Draw email if available
        if resume.email:
            c.setFont(style.normal_font[0], style.normal_font[1])
            c.setFillColor(style.text_color)
            c.drawString(left_column_x + border_padding, height - left_y - style.line_spacing, f"Email: {resume.email}")
            left_y += style.line_spacing

        left_y += style.line_spacing

        # Draw personal information section
        c.setFont(style.section_font[0], style.section_font[1])
        c.setFillColor(style.title_color)
        c.drawString(left_column_x + border_padding, height - left_y - style.line_spacing, "Личная информация")
        left_y += style.line_spacing

        # Draw personal details
        c.setFont(style.normal_font[0], style.normal_font[1])
        c.setFillColor(style.text_color)

        c.drawString(left_column_x + border_padding, height - left_y - style.line_spacing, f"Город: {resume.city}")
        left_y += style.line_spacing

        c.drawString(left_column_x + border_padding, height - left_y - style.line_spacing, f"Готов к переезду: {'Да' if resume.canRelocate else 'Нет'}")
        left_y += style.line_spacing

        if resume.citizenship:
            c.drawString(left_column_x + border_padding, height - left_y - style.line_spacing, f"Гражданство: {resume.citizenship}")
            left_y += style.line_spacing

        if resume.gender:
            c.drawString(left_column_x + border_padding, height - left_y - style.line_spacing, f"Пол: {resume.gender}")
            left_y += style.line_spacing

        c.drawString(left_column_x + border_padding, height - left_y - style.line_spacing, f"Дети: {'Есть' if resume.hasChildren else 'Нет'}")
        left_y += style.line_spacing

        if resume.languages:
            c.drawString(left_column_x + border_padding, height - left_y - style.line_spacing, f"Языки: {resume.languages}")
            left_y += style.line_spacing

        if resume.driverLicenses:
            c.drawString(left_column_x + border_padding, height - left_y - style.line_spacing, f"Вод. права: {resume.driverLicenses}")
            left_y += style.line_spacing

        c.drawString(left_column_x + border_padding, height - left_y - style.line_spacing, f"Мед. книжка: {'Есть' if resume.hasMedicalBook else 'Нет'}")
        left_y += style.line_spacing

        if resume.personalQualities:
            c.drawString(left_column_x + border_padding, height - left_y - style.line_spacing, f"Качества: {resume.personalQualities}")
            left_y += style.line_spacing

        # Draw right column
        right_y = y

        # Draw section border if enabled
        if style.decoration_config.draw_section_borders:
            c.setStrokeColor(style.decoration_config.border_color)
            c.rect(right_column_x, height - right_y - 450, right_column_width, 450)

        # Draw main information section
        c.setFont(style.section_font[0], style.section_font[1])
        c.setFillColor(style.title_color)
        c.drawString(right_column_x + border_padding, height - right_y - style.line_spacing, "Основная информация")
        right_y += style.line_spacing

        # Draw position
        c.setFont(style.normal_font[0], style.normal_font[1])
        c.setFillColor(style.text_color)
        c.drawString(right_column_x + border_padding, height - right_y - style.line_spacing, f"Должность: {resume.position}")
        right_y += style.line_spacing

        # Draw birth date if available
        if resume.birthDate:
            c.drawString(right_column_x + border_padding, height - right_y - style.line_spacing, f"Дата рождения: {resume.birthDate.strftime('%d.%m.%Y')}")
            right_y += style.line_spacing

        # Draw employment if available
        if resume.employment:
            c.drawString(right_column_x + border_padding, height - right_y - style.line_spacing, f"Занятость: {resume.employment}")
            right_y += style.line_spacing

        # Draw desired salary if available
        if resume.desiredSalary:
            c.drawString(right_column_x + border_padding, height - right_y - style.line_spacing, f"Зарплата: {resume.desiredSalary} руб.")
            right_y += style.line_spacing

        # Draw work schedule if available
        if resume.workSchedule:
            c.drawString(right_column_x + border_padding, height - right_y - style.line_spacing, f"График: {resume.workSchedule}")
            right_y += style.line_spacing

        # Draw business trips availability
        if resume.isReadyForTrips is not None:
            c.drawString(right_column_x + border_padding, height - right_y - style.line_spacing, f"Командировки: {'Да' if resume.isReadyForTrips else 'Нет'}")
            right_y += style.line_spacing

        # Add extra spacing
        right_y += style.line_spacing

        # Draw work experience section if available
        if hasattr(resume, 'work_experiences') and resume.work_experiences:
            # Draw section title
            c.setFont(style.section_font[0], style.section_font[1])
            c.setFillColor(style.title_color)
            c.drawString(right_column_x + border_padding, height - right_y - style.line_spacing, "Опыт работы")
            right_y += style.line_spacing

            # Draw each work experience entry
            c.setFont(style.normal_font[0], style.normal_font[1])
            c.setFillColor(style.text_color)
            
            for exp in resume.work_experiences:
                # Format period string
                period = f"с {exp.startDate.strftime('%m.%Y')} по {exp.endDate.strftime('%m.%Y') if exp.endDate else 'настоящее время'}"
                
                # Draw organization, position and period
                c.drawString(right_column_x + border_padding, height - right_y - style.line_spacing, 
                           f"{exp.organization} - {exp.position} ({period})")
                right_y += style.line_spacing

                # Draw responsibilities with extra indent
                if exp.responsibilities:
                    c.drawString(right_column_x + border_padding + 10, height - right_y - style.line_spacing,
                               exp.responsibilities)
                    right_y += style.line_spacing * 1.5

                right_y += style.line_spacing * 0.5

            # Add extra spacing after work experience section
            right_y += style.line_spacing

        # Draw education section if available
        if hasattr(resume, 'educations') and resume.educations:
            # Draw section title
            c.setFont(style.section_font[0], style.section_font[1])
            c.setFillColor(style.title_color)
            c.drawString(right_column_x + border_padding, height - right_y - style.line_spacing, "Образование")
            right_y += style.line_spacing

            # Draw each education entry
            c.setFont(style.normal_font[0], style.normal_font[1])
            c.setFillColor(style.text_color)

            for edu in resume.educations:
                # Draw institution, specialty and graduation year
                education_line = f"{edu.institution} - {edu.specialty} ({edu.graduationYear})"
                c.drawString(right_column_x + border_padding, height - right_y - style.line_spacing, education_line)
                right_y += style.line_spacing

                # Draw faculty if available
                if edu.faculty:
                    c.drawString(right_column_x + border_padding + 10, height - right_y - style.line_spacing,
                               f"Факультет: {edu.faculty}")
                    right_y += style.line_spacing

                # Draw study form if available
                if edu.studyForm:
                    c.drawString(right_column_x + border_padding + 10, height - right_y - style.line_spacing,
                               f"Форма обучения: {edu.studyForm}")
                    right_y += style.line_spacing

                right_y += style.line_spacing * 0.5
    else:
        # Draw main information section
        # y = style.margin_top
        y += style.line_spacing 

        # Draw section border if configured
        if style.decoration_config.draw_section_borders:
            section_start_y = y

        # Main Information Section
        c.setFont(style.section_font[0], style.section_font[1])
        c.setFillColor(style.title_color)
        c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, "Основная информация")
        y += style.line_spacing

        c.setFont(style.normal_font[0], style.normal_font[1])
        c.setFillColor(style.text_color)

        if resume.middleName:
            c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, f"Отчество: {resume.middleName}")
            y += style.line_spacing

        if resume.birthDate:
            c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, f"Дата рождения: {resume.birthDate.strftime('%d.%m.%Y')}")
            y += style.line_spacing

        if resume.phoneNumber:
            c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, f"Телефон: {resume.phoneNumber}")
            y += style.line_spacing

        if resume.email:
            c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, f"Email: {resume.email}")
            y += style.line_spacing

        c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, f"Должность: {resume.position}")
        y += style.line_spacing

        if resume.employment:
            c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, f"Занятость: {resume.employment}")
            y += style.line_spacing

        if resume.desiredSalary:
            c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, f"Зарплата: {resume.desiredSalary} руб.")
            y += style.line_spacing

        if resume.workSchedule:
            c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, f"График: {resume.workSchedule}")
            y += style.line_spacing

        c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, f"Командировки: {'Да' if resume.isReadyForTrips else 'Нет'}")
        y += style.line_spacing

        if style.decoration_config.draw_section_borders:
            section_height = y - section_start_y + border_padding
            if section_height > 0:
                c.setStrokeColor(style.decoration_config.border_color)
                c.rect(style.margin_left, height - section_start_y, width - style.margin_left - style.margin_right, -section_height)
                c.setStrokeColor(style.text_color)

        y += style.line_spacing

        # Personal Information Section
        if style.decoration_config.draw_section_borders:
            section_start_y = y

        c.setFont(style.section_font[0], style.section_font[1])
        c.setFillColor(style.title_color)
        c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, "Личная информация")
        y += style.line_spacing

        c.setFont(style.normal_font[0], style.normal_font[1])
        c.setFillColor(style.text_color)

        c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, f"Город: {resume.city}")
        y += style.line_spacing

        c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, f"Готов к переезду: {'Да' if resume.canRelocate else 'Нет'}")
        y += style.line_spacing

        if resume.citizenship:
            c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, f"Гражданство: {resume.citizenship}")
            y += style.line_spacing

        if resume.gender:
            c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, f"Пол: {resume.gender}")
            y += style.line_spacing

        c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, f"Дети: {'Есть' if resume.hasChildren else 'Нет'}")
        y += style.line_spacing

        if resume.languages:
            c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, f"Языки: {resume.languages}")
            y += style.line_spacing

        if resume.driverLicenses:
            c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, f"Вод. права: {resume.driverLicenses}")
            y += style.line_spacing

        c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, f"Мед. книжка: {'Есть' if resume.hasMedicalBook else 'Нет'}")
        y += style.line_spacing

        if resume.personalQualities:
            c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, f"Качества: {resume.personalQualities}")
            y += style.line_spacing

        if style.decoration_config.draw_section_borders:
            section_height = y - section_start_y + border_padding
            if section_height > 0:
                c.setStrokeColor(style.decoration_config.border_color)
                c.rect(style.margin_left, height - section_start_y, width - style.margin_left - style.margin_right, -section_height)
                c.setStrokeColor(style.text_color)

        y += style.line_spacing

        if y > height - 100:
            c.showPage()
            y = style.margin_top
            c.setFont(style.normal_font[0], style.normal_font[1])
            c.setFillColor(style.text_color)

        if resume.work_experiences:
            section_start_y = y

            c.setFont(style.section_font[0], style.section_font[1])
            c.setFillColor(style.title_color)
            c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, "Опыт работы")
            y += style.line_spacing

            c.setFont(style.normal_font[0], style.normal_font[1])
            c.setFillColor(style.text_color)

            for exp in resume.work_experiences:
                period = f"с {exp.startDate.strftime('%m.%Y')} по {exp.endDate.strftime('%m.%Y') if exp.endDate else 'настоящее время'}"
                c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, 
                            f"{exp.organization} - {exp.position} ({period})")
                y += style.line_spacing

                if exp.responsibilities:
                    c.drawString(style.margin_left + border_padding + 10, height - y - style.line_spacing,
                               exp.responsibilities)
                    y += style.line_spacing * 1.5

                y += style.line_spacing * 0.5

                if y > height - 100:
                    if style.decoration_config.draw_section_borders:
                        section_height = y - section_start_y + border_padding
                        if section_height > 0:
                            c.setStrokeColor(style.decoration_config.border_color)
                            c.rect(style.margin_left, height - section_start_y, 
                                  width - style.margin_left - style.margin_right, -section_height)
                            c.setStrokeColor(style.text_color)

                    c.showPage()
                    y = style.margin_top
                    c.setFont(style.normal_font[0], style.normal_font[1])
                    c.setFillColor(style.text_color)
                    section_start_y = y

            if style.decoration_config.draw_section_borders:
                section_height = y - section_start_y + border_padding
                if section_height > 0:
                    c.setStrokeColor(style.decoration_config.border_color)
                    c.rect(style.margin_left, height - section_start_y,
                          width - style.margin_left - style.margin_right, -section_height)
                    c.setStrokeColor(style.text_color)

            y += style.line_spacing

        if resume.educations:
            section_start_y = y

            c.setFont(style.section_font[0], style.section_font[1])
            c.setFillColor(style.title_color)
            c.drawString(style.margin_left + border_padding, height - y - style.line_spacing, "Образование")
            y += style.line_spacing

            c.setFont(style.normal_font[0], style.normal_font[1])
            c.setFillColor(style.text_color)

            for idx, edu in enumerate(resume.educations):
                c.drawString(style.margin_left + border_padding, height - y - style.line_spacing,
                            f"{edu.institution} - {edu.specialty} ({edu.graduationYear})")
                y += style.line_spacing

                if edu.faculty:
                    c.drawString(style.margin_left + border_padding + 10, height - y - style.line_spacing,
                               f"Факультет: {edu.faculty}")
                    y += style.line_spacing

                if edu.studyForm:
                    c.drawString(style.margin_left + border_padding + 10, height - y - style.line_spacing,
                               f"Форма обучения: {edu.studyForm}")
                    y += style.line_spacing

                y += style.line_spacing * 0.5

                if idx == len(resume.educations) - 1:
                    continue
                
                if y > height - 100:
                    if style.decoration_config.draw_section_borders:
                        section_height = y - section_start_y + border_padding
                        if section_height > 0:
                            c.setStrokeColor(style.decoration_config.border_color)
                            c.rect(style.margin_left, height - section_start_y,
                                  width - style.margin_left - style.margin_right, -section_height)
                            c.setStrokeColor(style.text_color)

                    c.showPage()
                    y = style.margin_top
                    c.setFont(style.normal_font[0], style.normal_font[1])
                    c.setFillColor(style.text_color)
                    section_start_y = y

            if style.decoration_config.draw_section_borders:
                section_height = y - section_start_y + border_padding
                if section_height > 0:
                    c.setStrokeColor(style.decoration_config.border_color)
                    c.rect(style.margin_left, height - section_start_y,
                          width - style.margin_left - style.margin_right, -section_height)
                    c.setStrokeColor(style.text_color)

            y += style.line_spacing

    ######

    c.save()
    buffer.seek(0)
    return buffer.getvalue()