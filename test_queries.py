from analysis.queries import listar_criptos, resumen_precios, buscar_por_nombre

print("Listado completo:")
print(listar_criptos())

print("Resumen de precios:")
print(resumen_precios())

print("Buscar Bitcoin:")
print(buscar_por_nombre("Bitcoin"))
