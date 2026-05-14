message = "4N1 MySSD EJ26 - 2043379 Emilio Dali"

dummy_text = (message * ( 125000 // len ( message ) + 1 )) [ : 125000 ]
byte_text = dummy_text.encode("utf8")

with open(r"EntornoDeSimulacion\mensaje.txt", "wb" ) as f:
    f.write (byte_text)

print (r"Mensaje creado en: EntornoDeSimulacion\mensaje.txt")