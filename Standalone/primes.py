# Really basic function that figures out how many prime numbers there are between any two numbers.

def prime(y,z):
	#y = 0
	first_y = y
	first_z = z
	check = True
	primes = []
	while check:
		x = 2
		y = int((y ** 0.5)+1)
		prime = True
		while x < y:
			if y % x == 0:
				prime = False
				break
			x+=1
		if y == 0 or y == 1:
			prime = False
		if prime:
			print (str(y) + " is prime!")
			primes.append(y)	
		y+=1
		if y == z+1:
			check = False
	print ("There are %i prime number(s) between %i and %i" % (len(primes),first_y,first_z))
	
prime(5,7)	
	