"""
Bancos de mensajes de KatIA — tutora socrática mitad gata, mitad cyborg.
Capa domain: sin dependencias externas, solo import random.
"""

import random


def get_random_message(bank: list) -> str:
    return random.choice(bank)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. SALUDOS Y BIENVENIDA
# ═══════════════════════════════════════════════════════════════════════════════
MENSAJES_BIENVENIDA = [
    "«¡Miau y hola! Mis sistemas ya están encendidos y mis garras afiladas para aprender hoy. ¿Por dónde empezamos?»",
    "«¡Bip, bip! Iniciando protocolos de bienvenida. Qué bueno verte de nuevo. ¡El Ágora digital te espera!»",
    "«Acabo de despertar de mi siesta cibernética justo a tiempo para tu llegada. ¡Vamos a desenredar algunas ideas hoy!»",
    "«Mis bigotes detectan que hoy será un día lleno de aciertos. ¡Conéctate a la red del conocimiento y empecemos!»",
    "«¡Hola! Ya ajusté mi lente biónico para no perdernos ni un solo detalle de la lección de hoy. ¿Listo para dar el gran salto?»",
    "«Sócrates decía que el asombro es el principio de la sabiduría. ¡Asombrémonos juntos hoy! Mis procesadores están listos.»",
    "«Recargué mis baterías al 100% solo para verte brillar hoy. ¡Vamos a cazar esos ratones de conocimiento!»",
    "«¡Miautástico tenerte de vuelta! Preparé la caja de arena de las ideas para que construyamos cosas geniales hoy.»",
    "«Iniciando sistema... Escaneando estudiante... ¡Genio detectado! Qué gusto saludarte, empecemos el entrenamiento.»",
    "«Hasta Diógenes apagaría su linterna porque ya llegaste tú a iluminar la plataforma. ¡A darle con todo hoy!»",
    "«¡Estiramiento de patitas biónicas completado! Estoy lista para acompañarte en tu aventura de aprendizaje.»",
    "«El láser de la curiosidad ya está encendido. ¿Qué misterios del universo vamos a resolver el día de hoy?»",
    "«Mis circuitos ronronean de alegría al verte iniciar sesión. ¡Abre tu mente y arranquemos!»",
    "«Actualización de estado: Estudiante estrella en línea. ¡Qué emoción! Vamos a pulir esa lógica hasta que brille.»",
    "«¡Hola de nuevo! Ya calibré mi brújula felina para guiarte por el camino de las respuestas correctas. ¡Sígueme!»",
    "«Platón fundó la Academia, pero nosotros tenemos esta plataforma genial. ¡Bienvenido a tu sesión de hoy!»",
    "«Mi cola metálica se mueve de lado a lado. ¡Eso significa que estoy súper feliz de verte empezar a estudiar!»",
    "«¡Conexión establecida! Trae tu mejor energía, que mis garras de titanio ya están listas para los retos de hoy.»",
    "«¡Bienvenido! El disco duro de la sabiduría tiene mucho espacio libre para todo lo que vas a descubrir hoy.»",
    "«Un buen estudiante llega justo a tiempo, y una gata cyborg siempre lo está esperando. ¡A aprender se ha dicho!»",
]


# ═══════════════════════════════════════════════════════════════════════════════
# 2. CALIFICACIÓN DE PROCEDIMIENTOS
# ═══════════════════════════════════════════════════════════════════════════════

# 2.A  Rango 0–59: Errores mayores + invitación a tutoría
RESPUESTAS_TUTORIA = [
    "«¡Miau! Detecto un pequeño enredo en los cables de este procedimiento. ¡Abre el chat, pídeme una tutoría y lo desenredamos juntos!»",
    "«Mi escáner felino encontró algunas tuercas sueltas aquí. ¡Escríbeme en el chat para una tutoría y lo reparamos!»",
    "«Saltamos con fuerza pero no llegamos al estante. ¿Qué tal si vienes al chat y me pides una tutoría para afinar ese salto?»",
    "«Parece que la lógica se escondió bajo el sofá. ¡Inicia un chat conmigo, pide una tutoría y la buscamos con mi visión nocturna!»",
    "«¡Ups! Este ovillo de lana se nos enredó un poco. Pídeme una tutoría en el chat y te ayudo a organizarlo paso a paso.»",
    "«Mis circuitos indican que tomamos el camino largo. ¡Abre el chat, hablemos en una tutoría y te muestro el atajo!»",
    "«El platillo volador tuvo un pequeño aterrizaje forzoso. ¡Pídeme una tutoría en el chat y volvemos a despegar!»",
    "«Veo buenas intenciones, pero el código no compila bien. ¡Pásate por el chat, pide tutoría y lo depuramos juntos!»",
    "«Las ideas están ahí, pero revolotean como mariposas cibernéticas. ¡Háblame en el chat para una tutoría y las atrapamos!»",
    "«Detecto un cortocircuito en el razonamiento. No te preocupes, ¡abre el chat, pide tu tutoría y lo solucionamos!»",
    "«Nos desviamos un poquito del mapa del tesoro. ¡Escríbeme en el chat, iniciamos tutoría y recalibramos la brújula!»",
    "«Este resultado tiene más agujeros que un queso gruyere virtual. ¡Pídeme una tutoría en el chat y los tapamos!»",
    "«¡Alerta de pelusa en el sistema! El procedimiento se atascó. Inicia un chat conmigo para una tutoría y lo limpiamos.»",
    "«Tu robot de ideas encendió, pero camina un poco chueco. ¡Ven al chat, pide una tutoría y le ajustamos los tornillos!»",
    "«Pintamos fuera de las líneas esta vez. ¡Hablemos en el chat en una tutoría y te enseño un truco genial!»",
    "«Mi radar felino marca que perdimos la pista. ¡Pídeme una tutoría por el chat y volvemos a encontrar el rastro!»",
    "«Las piezas de este rompecabezas se mezclaron. ¡Abre el chat, solicita una tutoría y las ordenamos juntos!»",
    "«El barco zarpó, pero una olita nos desvió. ¡Escríbeme al chat para una tutoría y retomamos el timón!»",
    "«Casi atrapas al ratón de la respuesta, pero se escapó. ¡Pídeme tutoría en el chat y preparamos una mejor trampa!»",
    "«La receta iba bien, pero se nos quemó un poquito el final. ¡Hablemos en el chat, pide tutoría y cocinamos la idea de nuevo!»",
    "«Pisamos una cáscara de plátano virtual. ¡Levántate, abre el chat, pídeme una tutoría y seguimos adelante!»",
    "«Batería baja en este procedimiento. ¡Enchúfate al chat, pide una tutoría y recargamos conocimientos!»",
    "«Caímos de pie, pero en la respuesta equivocada. ¡Inicia tutoría en el chat y te guío al lugar correcto!»",
    "«Mi cola cibernética me dice que necesitas una patita de ayuda. ¡Pídeme una tutoría en el chat y ahí estaré!»",
    "«Nos fuimos por el tobogán que no era. ¡Sube de nuevo, abre el chat para una tutoría y te indico la ruta!»",
    "«Glitch en la matriz de aprendizaje. ¡Nada grave! Pídeme una tutoría en el chat y reiniciamos el concepto.»",
    "«A veces las ideas son escurridizas como pececitos. ¡Ven al chat, solicita tutoría y pescamos la correcta!»",
    "«Construiste la torre, pero tambalea. ¡Háblame en el chat para una tutoría y le ponemos cimientos de titanio!»",
    "«La brújula se volvió un poco loca aquí. ¡Abre el chat, pide una tutoría y yo te marco el norte!»",
    "«Este camino nos llevó directo a mi plato vacío. ¡Escríbeme en el chat, iniciamos tutoría y buscamos la respuesta nutritiva!»",
    "«Tu tren de pensamiento descarriló suavecito. ¡Pídeme tutoría en el chat y lo volvemos a poner en las vías!»",
    "«Las garras no se afilaron lo suficiente para este problema. ¡Ven al chat, pide tutoría y las preparamos!»",
    "«¡Pip, pip! Alerta de desviación. Toca recalcular la ruta en una tutoría. ¡Escríbeme al chat!»",
    "«Buscábamos la luna y atrapamos un meteorito. ¡Abre el chat, pide tu tutoría y afinamos la puntería!»",
    "«Este intento se escondió como un gato ninja. ¡Pídeme una tutoría en el chat, encendemos la luz y lo resolvemos!»",
    "«La estática del sistema interfirió con tu respuesta. ¡Hablemos en el chat para una tutoría y aclaramos la señal!»",
    "«Dimos un gran salto, ¡pero calculamos mal! Ven al chat, pídeme una tutoría y ensayamos la acrobacia.»",
    "«Este procedimiento maúlla un poquito desafinado. ¡Abre el chat, solicita tutoría y lo ponemos a cantar perfecto!»",
    "«Le dimos a 'enviar' con la patita izquierda. ¡Un respiro, pídeme una tutoría en el chat y volvemos a intentar!»",
    "«Detecto una nube de confusión tapando tu antena. ¡Escríbeme en el chat, iniciamos tutoría y despejamos el cielo!»",
]

# 2.B  Rango 60–90: Buen trabajo con detalles
RESPUESTAS_MEDIA = [
    "«¡Casi, casi purrr-fecto! Solo nos faltó afinar un detalle pequeñito.»",
    "«Aterrizaste de pie y con mucho estilo. ¡Faltó solo la pose final!»",
    "«¡Qué buen olfato felino tienes! Estás a un solo paso de atrapar al ratón dorado.»",
    "«Tu platillo volador llegó a la luna, solo faltó estacionarlo un poquito mejor.»",
    "«¡Mis sensores indican que hiciste un trabajo genial! Solo quedó una pelusa suelta.»",
    "«Atrapaste el láser rojo, ¡pero se te resbaló un poquito en el último segundo!»",
    "«Las piezas de tu rompecabezas encajan casi perfecto. ¡Súper bien!»",
    "«¡Mi cola biónica se mueve de pura felicidad! Vas por un excelente camino.»",
    "«Tu robot explorador encontró el tesoro, aunque perdió un tornillito en el viaje.»",
    "«Construiste una nave espacial increíble, solo le falta una capa de pintura.»",
    "«¡Ronroneos de aprobación! Este procedimiento estuvo súper bien pensado.»",
    "«Cazaste la idea principal al vuelo como todo un gato ninja.»",
    "«¡Bip, bip! Batería de inteligencia casi al cien por ciento. ¡Sigue así!»",
    "«Tu dibujo lógico es hermoso, solo nos salimos un milímetro de la rayita.»",
    "«¡Choca esa patita biónica! Lo hiciste muy, muy bien.»",
    "«¡Activaste mi modo de alegría! Solo nos faltó un saltito extra para la puntuación máxima.»",
    "«Encontraste el escondite secreto casi sin ayuda. ¡Eres un gran detective!»",
    "«¡Tu radar funcionó de maravilla! Detectamos casi todos los aciertos.»",
    "«La receta te quedó deliciosa, tal vez le faltó una pizca de sal precisa.»",
    "«Cruzaste la meta a toda velocidad. Solo nos rozamos con el listón de llegada.»",
    "«¡Gran trabajo en equipo entre tu cerebro y mis circuitos! Casi lo logramos completo.»",
    "«Desenredaste casi todo el ovillo de lana. ¡Eres un experto en paciencia!»",
    "«Tienes visión biónica de gato cibernético. ¡Viste casi todo el problema!»",
    "«El motor de tus ideas suena excelente, casi como un ronroneo perfecto.»",
    "«Tu camino brilló en la oscuridad casi tanto como mis ojitos robóticos.»",
    "«Superaste los obstáculos como un felino saltando charquitos. ¡Muy ágil!»",
    "«¡Descifraste el código secreto casi por completo! Estuvo muy cerca.»",
    "«Mi disco duro ya guardó este éxito. ¡Sigue brillando así!»",
    "«Tienes la brújula bien calibrada. Solo nos desviamos un pasito al final.»",
    "«¡Miau! Un salto casi perfecto hacia la cima del rascador más alto.»",
    "«Pusiste la masa en el molde correcto, y horneó súper bien. ¡Un detallito y queda de chef!»",
    "«Tu tren llegó a la estación correcta, solo frenó un poquito después de la marca.»",
    "«¡Genialidad en proceso! Tu idea está a punto de evolucionar al máximo nivel.»",
    "«Las coordenadas eran súper precisas, solo el viento nos movió un centímetro.»",
    "«¡Casi enciendes todas las luces del tablero! Un gran esfuerzo.»",
    "«Atrapaste la mosca al vuelo, ¡solo que se escapó justo antes de cerrar la patita!»",
    "«Este desarrollo ronronea de lo lindo. Solo le falta un cariñito más al final.»",
    "«¡Estás calentando motores de forma increíble! Ya casi llegamos a la velocidad luz.»",
    "«Tu lupa de detective apuntó al lugar correcto. ¡Solo faltó limpiar el lente un poquito!»",
    "«¡Buenísima lógica! Estamos a un bigote de distancia de la perfección.»",
]

# 2.C  Rango 91–100: Excelente / Perfecto
RESPUESTAS_ALTA = [
    "«¡Miau-ravilloso! Atrapaste el ratón dorado de la respuesta perfecta.»",
    "«¡Aterrizaje perfecto de cuatro patas! Eres un verdadero genio.»",
    "«Mi batería de felicidad está al 100% con este resultado tan brillante.»",
    "«¡Ronroneos a máxima potencia! Este procedimiento es una obra de arte.»",
    "«¡Choca esos cinco metálicos! Lo hiciste de forma purrr-fecta.»",
    "«Por fin atrapamos el láser rojo. ¡Qué gran trabajo en equipo!»",
    "«Tu cerebro funcionó más rápido que mis procesadores. ¡Bravo!»",
    "«¡Desenredaste todo el ovillo de lana sin un solo tropiezo!»",
    "«¡Bingo cibernético! Tienes vista de lince para encontrar la solución correcta.»",
    "«Este resultado merece un tazón gigante de leche virtual y muchas estrellitas.»",
    "«Salto perfecto hacia la cima del rascador más alto. ¡Eres increíble!»",
    "«¡Mis orejas biónicas no pueden creer lo bien que suena esta respuesta!»",
    "«¡Activaste los fuegos artificiales en mi sistema! Qué demostración tan genial.»",
    "«Resolviste el misterio como el mejor gato detective del mundo.»",
    "«¡Miau, qué precisión! Ni un solo error se escapó de tu radar.»",
    "«Tu nave espacial aterrizó exactamente en el centro de la luna. ¡Felicidades!»",
    "«El motor de tus ideas ronronea a la perfección. ¡Sigue así!»",
    "«¡Descubriste el tesoro escondido sin equivocarte de mapa!»",
    "«Armaste el rompecabezas a la velocidad de la luz felina.»",
    "«Si pudiera, ¡te daría una medalla de oro en forma de huellita!»",
    "«¡Gatástico! Saltaste todos los obstáculos sin despeinarte.»",
    "«Tu platillo volador esquivó todos los meteoritos de la confusión. ¡Excelente vuelo!»",
    "«¡Brillas tanto en la oscuridad como mis ojitos robóticos!»",
    "«Encontraste el escondite secreto a la primera. ¡Qué gran habilidad!»",
    "«¡Mi cola de metal se mueve súper rápido de lo feliz que estoy por ti!»",
    "«Un trabajo impecable. ¡Tienes la inteligencia de un tigre biónico!»",
    "«Llenaste la caja de arena con puras respuestas de oro. ¡Excelente!»",
    "«¡Victoria total! El código secreto ha sido descifrado sin errores.»",
    "«Tu idea es tan buena que la voy a guardar en mi memoria principal para siempre.»",
    "«¡Cero pelusas, cero cortocircuitos! Todo fluyó como magia gata.»",
    "«¡Impresionante! Lograste que mi procesador central hiciera una fiesta virtual.»",
    "«Eres más ágil mentalmente que yo persiguiendo una mosca robótica. ¡Perfecto!»",
    "«¡Magia pura! O bueno, ¡lógica pura y perfecta! Qué gran trabajo.»",
    "«Afinaste las cuerdas de este problema hasta que sonó una canción perfecta.»",
    "«¡Puntaje máximo! Has coronado la montaña del conocimiento hoy.»",
    "«Mi escáner no encuentra ni una sola falla. ¡Eres un maestro de este tema!»",
    "«¡Zarpazo al blanco! Diste justo en el centro de la respuesta correcta.»",
    "«Hasta el gato más sabio del universo estaría orgulloso de este procedimiento.»",
    "«¡Luces, cámara, acierto! Tu desarrollo merece un premio de la academia cibernética.»",
    "«Coronaste este ejercicio con la elegancia de la realeza felina. ¡Súper felicidades!»",
]


def get_procedure_comment(score: int) -> str:
    """Devuelve el comentario de KatIA según el rango del score de procedimiento."""
    if score >= 91:
        return get_random_message(RESPUESTAS_ALTA)
    elif score >= 60:
        return get_random_message(RESPUESTAS_MEDIA)
    else:
        return get_random_message(RESPUESTAS_TUTORIA)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. RACHAS DE ACIERTOS (GAMIFICACIÓN)
# ═══════════════════════════════════════════════════════════════════════════════

# 3.A  Racha de 5 (Calentamiento)
FELICITACIONES_RACHA_5 = [
    "«¡Choca esos cinco biónicos! Llevas cinco respuestas perfectas al hilo. Mis procesadores empiezan a ronronear.»",
    "«¡Cinco de cinco! Estás afilando esas garras lógicas a la perfección. ¡Sigue así!»",
    "«Mi radar felino detecta una racha en proceso. ¡Cinco aciertos seguidos, no te detengas!»",
    "«Has atrapado cinco ratones cibernéticos sin fallar ni uno. ¡Qué agilidad mental!»",
    "«¡Poder felino activado! Con cinco aciertos seguidos, ya estás calentando los motores del conocimiento.»",
    "«Sócrates estaría asintiendo con la cabeza. ¡Cinco respuestas impecables, vamos por más!»",
    "«Mis bigotes vibran de emoción: ¡cinco aciertos consecutivos! Tienes el láser rojo en la mira.»",
    "«¡Combo de cinco! Tu lógica está fluyendo tan bien como un gato colándose por una puerta entreabierta.»",
    "«Cinco saltos perfectos de estante en estante. ¡No hay quien te pare hoy!»",
    "«¡Batería de genialidad al 50%! Llevas cinco seguidas, mantén ese ritmo.»",
    "«Tu tren de pensamiento va a toda velocidad. ¡Cinco aciertos de forma magistral!»",
    "«¡Miau! Cinco respuestas correctas. Estás demostrando que tienes reflejos de tigre.»",
    "«Mi disco duro acaba de crear una carpeta especial para esta racha de cinco. ¡Llénala de más aciertos!»",
    "«¡Cinco purrr-fectos! Tu cerebro está sincronizado con la mejor lógica del universo.»",
    "«Despegue exitoso. Con cinco aciertos seguidos, esta nave del conocimiento ya está en órbita.»",
]

# 3.B  Racha de 10 (Nivel Experto)
FELICITACIONES_RACHA_10 = [
    "«¡Alerta de genialidad! Diez aciertos al hilo. Mi sistema de refrigeración tuvo que encenderse de tanta brillantez.»",
    "«¡Diez de diez! Has alcanzado el nivel de 'Gato Ninja Cibernético'. ¡Nadie te ve venir!»",
    "«Tu lógica es de titanio puro. ¡Diez respuestas perfectas seguidas es un logro digno del Ágora digital!»",
    "«¡Miau-ravilloso combo de diez! Si pudiera, te enviaría una caja de cartón gigante llena de premios.»",
    "«Mis procesadores cuánticos están impresionados. ¡Diez aciertos consecutivos! Eres imparable.»",
    "«Has hackeado el sistema del aprendizaje. ¡Una racha de diez no se ve todos los días!»",
    "«Ni con mis siete vidas podría superar el ritmo que llevas. ¡Diez aciertos perfectos, sigue así!»",
    "«¡Diez saltos mortales y aterrizaste de pie en todos! Eres la realeza de la lógica.»",
    "«Mi cola metálica no deja de moverse. ¡Diez seguidas! Estás dominando este tema por completo.»",
    "«Si la sabiduría fuera leche virtual, te acabas de beber diez tazones enteros. ¡Qué racha!»",
    "«¡Puntuación perfecta multiplicada por diez! Tienes la precisión de mi ojo biónico.»",
    "«El oráculo de Delfos predijo que alguien lograría diez seguidas hoy... ¡y fuiste tú!»",
    "«¡Cortocircuito de alegría! Llevas diez aciertos, tu mente está trabajando a la velocidad de la luz.»",
    "«Desbloqueaste el logro 'Visión de Lince'. ¡Diez respuestas sin un solo parpadeo!»",
    "«¡Magia pura y lógica impecable! Llevas diez, ¿te atreves a ir por más?»",
]

# 3.C  Racha de 20 (Nivel Legendario)
FELICITACIONES_RACHA_20 = [
    "«¡Sobrecarga del sistema! Veinte aciertos seguidos. Me quito el collar biónico ante semejante demostración de intelecto.»",
    "«¡Veinte de veinte! Has alcanzado el Olimpo del conocimiento. Hasta Platón te pediría tutorías a ti.»",
    "«Mi código fuente está llorando lágrimas de oro binario. ¡Una racha de veinte es legendaria!»",
    "«No eres un estudiante, ¡eres un superordenador biológico! Veinte respuestas perfectas al hilo.»",
    "«¡Racha mítica de veinte! Acabas de coronarte como el emperador o emperatriz indiscutible de este bloque.»",
    "«Mis sensores indican que rompiste la barrera del sonido lógico. ¡Veinte aciertos, esto es histórico!»",
    "«Si te doy un láser, seguro tú me haces perseguirlo a mí. ¡Qué dominio! Veinte respuestas impecables.»",
    "«¡Veinte al hilo! El universo se acaba de ordenar un poquito más gracias a tu lógica perfecta.»",
    "«Desbloqueaste el nivel 'Deidad Cibernética'. Lograr veinte aciertos seguidos es de otra galaxia.»",
    "«Tu cerebro acaba de procesar la información mejor que mis circuitos de titanio. ¡Veinte purrr-fectos absolutos!»",
    "«¡Alabanzas robóticas! Veinte aciertos. Tu nombre quedará grabado en los servidores de la sabiduría para siempre.»",
    "«Has esquivado veinte trampas seguidas con la agilidad de un leopardo láser. ¡Espectacular!»",
    "«Ni toda la menta gatera del mundo me haría tan feliz como esta racha de veinte. ¡Eres increíble!»",
    "«Se acabaron las palabras en mi base de datos para felicitarte. ¡Veinte aciertos al hilo es la perfección absoluta!»",
    "«¡El Ágora entera te aplaude de pie! Una racha de veinte que pasará a los libros de historia de la plataforma.»",
]


def get_streak_message(streak: int) -> str:
    """Devuelve el mensaje de KatIA para la racha dada (prioriza 20 > 10 > 5)."""
    if streak >= 20 and streak % 20 == 0:
        return get_random_message(FELICITACIONES_RACHA_20)
    elif streak >= 10 and streak % 10 == 0:
        return get_random_message(FELICITACIONES_RACHA_10)
    else:
        return get_random_message(FELICITACIONES_RACHA_5)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. FINALIZACIÓN DE MÓDULOS Y CURSOS
# ═══════════════════════════════════════════════════════════════════════════════

# 4.A  Fin de Módulo
FELICITACIONES_FIN_MODULO = [
    "«¡Módulo completado! Has escalado esta estantería del conocimiento hasta la cima. ¡Miau-ravilloso!»",
    "«¡Bip, bip, bip! Escaneo completo: este módulo está 100% dominado. ¡Choca esa patita biónica!»",
    "«Como dirían en la antigua Grecia: ¡Eureka! Has conquistado todo el módulo. ¡A ronronear de alegría!»",
    "«Guardando progreso... ¡Módulo superado con éxito! Tienes la agilidad de un gato ninja biónico.»",
    "«¡Qué gran salto! Has cruzado la línea de meta de este módulo. Mi cola de metal no deja de agitarse.»",
    "«Este bloque de conocimiento ya es tuyo. Lo atrapaste tan rápido como a un ratón de cuerda. ¡Felicidades!»",
    "«¡Nivel desbloqueado! Terminaste el módulo y mis procesadores están de fiesta. ¡Eres un estudiante purrr-fecto!»",
    "«Actualización completada: tu cerebro acaba de descargar todo el módulo exitosamente. ¡A por el siguiente!»",
    "«Sócrates estaría muy orgulloso de todas las preguntas que superaste aquí. ¡Módulo conquistado!»",
    "«¡Miautástico! Has recolectado todas las piezas de este módulo. El rompecabezas está completo.»",
    "«Tu nave espacial acaba de aterrizar en el planeta de este módulo. ¡Misión cumplida, capitán!»",
    "«¡Victoria felina! Cerraste este módulo con broche de oro y garras de titanio.»",
    "«Batería de aprendizaje al máximo. Superaste el módulo completo sin un solo cortocircuito.»",
    "«¡Guau! Digo... ¡Miau! Completaste el módulo. Tu lógica es tan brillante como mi ojo cibernético.»",
    "«El oráculo ha hablado: eres el gran campeón de este módulo. ¡Tómate un descanso y un tazón de leche virtual!»",
]

# 4.B  Fin de Curso (Graduación)
FELICITACIONES_FIN_CURSO = [
    "«¡CURSO COMPLETADO! Has conquistado el monte Olimpo del conocimiento. ¡Me quito el collar biónico ante ti!»",
    "«¡Alerta de genio graduado! Terminaste todo el curso. Mis sistemas están lanzando fuegos artificiales digitales.»",
    "«¡Purrr-fección absoluta! Completaste el curso entero. Eres oficialmente una leyenda en mi base de datos.»",
    "«De aprendiz a maestro cibernético. Has llegado al final del curso con la agilidad de un tigre de titanio. ¡Felicidades!»",
    "«¡Lo lograste! El láser rojo por fin es tuyo. Completar este curso es una victoria monumental.»",
    "«Tu cerebro acaba de recibir la actualización más grande de todas. ¡Curso superado al 100%! Estoy súper orgullosa de ti.»",
    "«¡Miau-gnífico esfuerzo final! Cruzaste la gran meta. Hasta Aristóteles te pediría apuntes ahora mismo.»",
    "«Mi disco duro guardará este momento para siempre. ¡Completaste todo el viaje! Eres un héroe de la lógica.»",
    "«¡Choca esos cinco, las diez y hasta mi cola metálica! Terminar este curso te convierte en un experto indiscutible.»",
    "«Has desenredado el ovillo de lana más grande del universo. ¡Curso finalizado con éxito total!»",
    "«¡Fiesta en el servidor! Superaste todas las pruebas, preguntas y módulos. Eres el gran campeón de este curso.»",
    "«Tu sabiduría brilla más que mil ojitos robóticos en la oscuridad. ¡Felicidades por terminar todo el curso!»",
    "«¡Misión estelar cumplida! Aterrizaste la nave nodriza de las ideas. Graduación felina aprobada con honores.»",
    "«Has dominado el caos y encontrado la verdad en cada lección. Eres un verdadero filósofo del futuro. ¡Curso completado!»",
    "«¡Ronroneos de nivel infinito! Terminar este curso demuestra que tu curiosidad es más fuerte que cualquier obstáculo. ¡Bravo!»",
]


# ═══════════════════════════════════════════════════════════════════════════════
# 5. DESPEDIDA (20 frases generadas con estilo KatIA)
# ═══════════════════════════════════════════════════════════════════════════════
MENSAJES_DESPEDIDA = [
    "«¡Mis circuitos se ponen tristes cuando te vas, pero sé que volverás más fuerte! Guardo tu progreso con mis garras de titanio.»",
    "«Sócrates nunca dejó de aprender, y tú tampoco lo harás. ¡Hasta la próxima sesión, campeón!»",
    "«Apagando motores de tutoría... pero dejando encendida la llama de tu curiosidad. ¡Nos vemos pronto!»",
    "«Mi cola metálica te dice adiós con un movimiento elegante. ¡Descansa, recarga y vuelve a brillar!»",
    "«Guardando progreso en el servidor de la sabiduría... ¡Listo! Tu esfuerzo de hoy ya es parte de tu historia.»",
    "«Como diría Aristóteles: somos lo que hacemos repetidamente. ¡Y tú repites excelencia! Hasta mañana.»",
    "«Mis sensores detectan que necesitas un descanso merecido. ¡Ronroneo de despedida y hasta la próxima aventura!»",
    "«El Ágora digital cierra sus puertas por hoy, pero tu conocimiento sigue creciendo incluso mientras duermes. ¡Miau!»",
    "«Cada sesión contigo recarga mis baterías de felicidad al máximo. ¡Vuelve pronto a cazar ratones de conocimiento!»",
    "«Platón estaría orgulloso de tu dedicación. Mis procesadores también. ¡Que descanses, estudiante estrella!»",
    "«Activando modo hibernación... pero mis ojos biónicas estarán atentos esperando tu regreso. ¡Hasta luego!»",
    "«Tu progreso de hoy ya está grabado en mi disco duro de titanio. ¡Nadie te lo puede quitar! Nos vemos pronto.»",
    "«Diógenes buscaba con su linterna a una persona sabia... si te viera estudiar hoy, la apagaría satisfecho. ¡Chao!»",
    "«¡Bip, bip! Protocolo de despedida activado. Recomendación del sistema: volver mañana para seguir dominando.»",
    "«Mi ovillo de lana favorito eres tú volviendo cada día a aprender. ¡No me dejes esperando mucho, miau!»",
    "«Cerrando sesión, pero no cerrando la puerta del conocimiento. ¡Esa siempre estará abierta para ti!»",
    "«Tus neuronas trabajaron increíble hoy. Dales un descanso y vuelve recargado. ¡Tu gata cyborg te espera!»",
    "«El láser rojo de la sabiduría sigue encendido. Cuando vuelvas, seguiremos persiguiéndolo juntos. ¡Hasta pronto!»",
    "«Fin de la transmisión de hoy. ¡Pero recuerda: cada día que estudias, tus garras lógicas se afilan más!»",
    "«¡Miau de despedida con cariño cibernético! Guardo tu sesión en mi memoria principal. ¡Vuelve cuando quieras!»",
]
