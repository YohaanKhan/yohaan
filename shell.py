import yohaan

while True:
    text = input('yohaan >')
    result, error = yohaan.run(text)
     
    if error:
        print(error.as_string())
    else:
        print(result)