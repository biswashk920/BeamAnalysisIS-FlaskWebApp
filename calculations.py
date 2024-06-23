import math

def calculate_moment_and_shear(total_load, span):
    factored_load_intensity = 1.5 * total_load  # kN/m (factored load for limit state design)
    max_moment = (factored_load_intensity * span ** 2) / 8  # kN.m
    max_shear = (factored_load_intensity * span) / 2  # kN
    return max_moment, max_shear

def suggest_beam_dimensions(max_depth, max_width):
    dimensions = []
    for depth in range(300, min(1050, int(max_depth) + 50), 50):  # depths from 300 mm to max_depth
        for width in range(150, min(550, int(max_width) + 50), 50):  # widths from 150 mm to max_width
            dimensions.append({"depth": depth, "width": width})
    return dimensions

def calculate_steel_reinforcement(depth, width, max_moment, grade_concrete, grade_steel):
    partial_safety_factor_concrete = 1.5
    partial_safety_factor_steel = 1.15

    effective_depth = depth - 50  # mm (assuming 50 mm cover)
    f_ck = grade_concrete  # N/mm²
    f_y = grade_steel  # N/mm²

    gross_area = width * depth
    min_area_steel = 0.85 / 100 * gross_area
    max_area_steel = 4 / 100 * gross_area

    # Moment of resistance calculation
    lever_arm = 0.87 * effective_depth  # mm
    limiting_area_steel = 0.36 * f_ck * width * effective_depth / f_y

    # Required area of steel
    required_area_steel = max_moment * 1e6 / (0.87 * f_y * lever_arm)  # mm²

    # Adjusting to min/max limits
    required_area_steel = max(min_area_steel, min(max_area_steel, required_area_steel))

    if required_area_steel <= limiting_area_steel:  # Under-reinforced or balanced section
        moment_capacity_steel = (0.87 * f_y * required_area_steel * lever_arm) / partial_safety_factor_steel  # N.mm
        moment_capacity_concrete = (0.36 * f_ck * width * effective_depth ** 2) / partial_safety_factor_concrete  # N.mm
        total_moment_capacity = moment_capacity_steel + moment_capacity_concrete  # N.mm
    else:  # Over-reinforced section
        total_moment_capacity = (0.87 * f_y * required_area_steel * lever_arm) / partial_safety_factor_steel  # N.mm

    total_moment_capacity_kNm = total_moment_capacity * 1e-6  # converting N.mm to kN.m

    return required_area_steel, total_moment_capacity_kNm

def determine_rebar_details(required_area_steel, width, effective_depth, grade_steel):
    rebar_diameters = [40, 32, 25, 20, 16, 12, 10, 8]  # in mm, sorted from larger to smaller

    for dia in rebar_diameters:
        area_single_rebar = math.pi * (dia / 2) ** 2  # mm²
        num_rebars = math.ceil(required_area_steel / area_single_rebar)

        # Check if the rebars fit within the beam width
        if num_rebars * dia * 1.25 < width:  # 1.25 is a spacing factor
            spacing = (width - num_rebars * dia) / (num_rebars + 1)
            return dia, num_rebars, spacing, effective_depth

    # If none of the diameters fit, return the details for the minimum diameter
    dia = rebar_diameters[-1]
    area_single_rebar = math.pi * (dia / 2) ** 2  # mm²
    num_rebars = math.ceil(required_area_steel / area_single_rebar)
    spacing = (width - num_rebars * dia) / (num_rebars + 1)

    return dia, num_rebars, spacing, effective_depth

def calculate_tie_bars(span, depth, effective_depth, max_shear, grade_steel):
    stirrup_diameters = [8, 10]  # possible diameters for stirrups
    min_shear_reinforcement = 0.4 / 100 * depth * effective_depth  # minimum shear reinforcement area as per IS 456

    for stirrup_diameter in stirrup_diameters:
        area_single_stirrup = math.pi * (stirrup_diameter / 2) ** 2  # mm²
        two_legged_area = 2 * area_single_stirrup  # as it is a 2-legged stirrup

        # Shear force carried by concrete
        f_y = grade_steel  # N/mm²
        shear_force_concrete = 0.4 * depth * effective_depth * 0.87 * f_y * 1e-3  # kN

        if max_shear > shear_force_concrete:
            additional_shear = max_shear - shear_force_concrete  # kN
            stirrup_spacing = two_legged_area * 0.87 * f_y * effective_depth * 1e-3 / additional_shear  # mm

            if stirrup_spacing < min(0.75 * effective_depth, 300):  # IS 456:2000 guidelines
                stirrup_spacing = min(0.75 * effective_depth, 300)  # mm

            num_stirrups = math.ceil(span * 1000 / stirrup_spacing)  # converting span to mm and calculating total stirrups
            return stirrup_diameter, num_stirrups, stirrup_spacing

    # If no additional shear reinforcement is needed, provide minimum shear reinforcement
    min_spacing = min(0.75 * effective_depth, 300)  # default spacing
    num_stirrups = math.ceil(span * 1000 / min_spacing)
    return 8, num_stirrups, min_spacing  # default to 8mm stirrups with minimum spacing

def evaluate_beams(beams):
    max_strength_beam = max(beams, key=lambda x: x['total_moment_capacity'])
    min_cost_beam = min(beams, key=lambda x: x['required_area_steel'])
    return max_strength_beam, min_cost_beam

def recommend_grade_upgrade():
    return "The provided beam dimensions are excessive. Consider increasing the grade of concrete and steel."

def check_width_depth_ratio(width, depth):
    ratio = width / depth
    return 0.3 <= ratio <= 0.5

def beam_design(total_load, span, grade_concrete, grade_steel, max_depth, max_width):
    max_moment, max_shear = calculate_moment_and_shear(total_load, span)
    dimensions = suggest_beam_dimensions(max_depth, max_width)

    beams_singly = []
    beams_doubly = []
    for dim in dimensions:
        depth = dim["depth"]
        width = dim["width"]
        required_area_steel, total_moment_capacity = calculate_steel_reinforcement(depth, width, max_moment, grade_concrete, grade_steel)
        beams_singly.append({
            "depth": depth,
            "width": width,
            "required_area_steel": required_area_steel,
            "total_moment_capacity": total_moment_capacity
        })

    max_strength_beam_singly, min_cost_beam_singly = evaluate_beams(beams_singly)

    if max_strength_beam_singly['total_moment_capacity'] < max_moment:
        return recommend_grade_upgrade()

    rebar_diameter, num_rebars, rebar_spacing, effective_depth = determine_rebar_details(
        min_cost_beam_singly['required_area_steel'],
        min_cost_beam_singly['width'],
        min_cost_beam_singly['depth'],
        grade_steel)

    stirrup_diameter, num_stirrups, stirrup_spacing = calculate_tie_bars(
        span,
        min_cost_beam_singly['depth'],
        effective_depth,
        max_shear,
        grade_steel)

    if not check_width_depth_ratio(min_cost_beam_singly['width'], min_cost_beam_singly['depth']):
        return "Width to depth ratio is not satisfactory. Please adjust dimensions."

    result = {
        "depth": min_cost_beam_singly['depth'],
        "width": min_cost_beam_singly['width'],
        "required_area_steel": min_cost_beam_singly['required_area_steel'],
        "total_moment_capacity": min_cost_beam_singly['total_moment_capacity'],
        "rebar_diameter": rebar_diameter,
        "num_rebars": num_rebars,
        "rebar_spacing": rebar_spacing,
        "stirrup_diameter": stirrup_diameter,
        "num_stirrups": num_stirrups,
        "stirrup_spacing": stirrup_spacing
    }

    return result
