from tutorials import pattern_generator

list_diameters = [0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3]
excentricity_min_max = (0.6, 0.9)
diameter_percetage_clearence_min_max = (0.3, 0.3)
MINOR_AXIS_SIZE_IN_MM = 1
pattern_generator = pattern_generator.PatternGenerator(MINOR_AXIS_SIZE_IN_MM,
                                                       list_diameters,
                                                       excentricity_min_max,
                                                       diameter_percetage_clearence_min_max)

list_patterns = pattern_generator.generate()

primitive_group_container_plots = []
for pattern in list_patterns[:1]:
    pattern.plot_pattern().plot()
# pattern_generator.get_elipse_interpolation()
