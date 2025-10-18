def normalize(angle):
	return (angle + 180) % 360 - 180

def threshold(angle, target, threshold):
	diferencia = angle - target

	diferencia_normalizada = (diferencia + 180) % 360 - 180

	return abs(diferencia_normalizada) <= threshold