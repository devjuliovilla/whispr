Quiero extender el proyecto Whispr instalado en:

C:\tools\whispr

OBJETIVO GENERAL

Convertir Whispr en una herramienta de dictado inteligente completamente local, similar en concepto a Typeless/Wispr Flow, utilizando:

- faster-whisper para speech-to-text.
- large-v3-turbo como modelo actual.
- CUDA con mi NVIDIA RTX 5060 Laptop de 8 GB.
- Ollama para procesamiento inteligente posterior a la transcripción.
- Windows 11.
- Todo debe funcionar localmente, sin APIs externas ni servicios de pago.

IMPORTANTE

Antes de modificar código:

1. Analiza completamente el proyecto actual.
2. Revisa su arquitectura, configuración, formatter, hotkeys, listener, inyección de texto, tests y launcher.
3. Identifica los cambios locales que ya existen.
4. Ejecuta o revisa los tests existentes.
5. Propón primero un plan de implementación.
6. NO empieces una refactorización grande sin justificarla.
7. NO rompas el flujo actual, que ya funciona correctamente.

ESTADO ACTUAL FUNCIONAL

Actualmente Whispr funciona correctamente:

- Modelo: large-v3-turbo.
- GPU/CUDA funcionando.
- Idioma de reconocimiento: español.
- Hotkey principal: F8.
- Modo de hotkey: hold/push-to-talk.
- Se ejecuta desde la bandeja del sistema.
- Puede iniciar automáticamente con Windows.
- La transcripción se pega en la aplicación activa.
- spoken_commands está habilitado.

La configuración está en:

%APPDATA%\Whispr\config.json

La GUI de Settings NO es accesible adecuadamente con NVDA, por lo que no debemos depender exclusivamente de ella para configurar nuevas funcionalidades.

CAMBIOS LOCALES QUE YA HICIMOS

1. run_whispr.pyw fue modificado para agregar automáticamente al PATH del proceso las DLL de CUDA instaladas dentro del virtualenv:

.venv\Lib\site-packages\nvidia\cublas\bin
.venv\Lib\site-packages\nvidia\cudnn\bin

Esto permite que faster-whisper/CTranslate2 encuentre cublas64_12.dll y cudnn64_9.dll sin modificar globalmente el PATH de Windows.

Existe un backup:

run_whispr.pyw.bak

2. whispr\formatter.py fue modificado para que spoken_commands reconozca también comandos en español.

Actualmente reconoce, además de los comandos originales en inglés:

- salto de línea
- nueva línea
- nuevo párrafo
- salto de párrafo

Se aceptan variantes con y sin acentos.

Existe un backup:

whispr\formatter.py.bak

Estos cambios funcionan y deben conservarse.

NO quiero continuar creando un parser enorme basado en regex para interpretar lenguaje natural.

ARQUITECTURA DESEADA

Quiero separar dos responsabilidades:

A. FORMATTER DETERMINISTA

Debe encargarse únicamente de operaciones simples, inequívocas y rápidas.

Ejemplos:

- salto de línea
- nueva línea
- nuevo párrafo
- puntuación simple si resulta conveniente
- replacements
- dictionary
- limpieza existente

No implementar aquí lógica compleja para comprender intención.

B. PROCESAMIENTO INTELIGENTE

Después de obtener la transcripción de Whisper, quiero opcionalmente enviarla a un modelo local mediante Ollama.

Flujo conceptual:

Micrófono
  ->
faster-whisper / large-v3-turbo
  ->
transcripción
  ->
formatter determinista
  ->
procesamiento inteligente con Ollama
  ->
texto final
  ->
inyección en la aplicación activa

El procesamiento con Ollama debe ser OPCIONAL y debe existir siempre una ruta que funcione sin Ollama.

FUNCIONALIDAD DE DICTADO INTELIGENTE

El modelo debe recibir instrucciones estrictas para transformar una transcripción hablada en texto listo para insertar.

Debe:

1. Mantener la intención del usuario.

2. Corregir puntuación y capitalización.

3. Eliminar muletillas cuando corresponda.

Ejemplos:

eh
este
mmm
em
etc.

4. Resolver falsos comienzos y autocorrecciones habladas.

Ejemplo:

"Mañana nos vemos a las tres... no, perdón, mejor a las cuatro."

Resultado:

"Mañana nos vemos a las cuatro."

Otro ejemplo:

"El endpoint está en users... no, perdón, payments."

Resultado:

"El endpoint está en payments."

5. Interpretar instrucciones de formato.

Ejemplo:

"haz una lista con comprar leche, llamar a Juan y revisar Mercado Pago"

Resultado:

- Comprar leche
- Llamar a Juan
- Revisar Mercado Pago

Ejemplo:

"lista numerada, primero configurar la API, segundo probar el webhook, tercero hacer deploy"

Resultado:

1. Configurar la API.
2. Probar el webhook.
3. Hacer deploy.

6. Interpretar instrucciones como:

- haz una lista
- lista numerada
- lista con viñetas
- nuevo párrafo
- siguiente elemento
- etc.

No quiero depender de frases exactas siempre que el modelo pueda inferir claramente la intención.

7. Conservar términos técnicos.

Ejemplos importantes:

.NET
ASP.NET
C#
PowerShell
JavaScript
TypeScript
React
React Native
Angular
SQL Server
Azure
Azure DevOps
Git
GitHub
OpenCode
Claude Code
Codex
Ollama
Mercado Pago
WebView
webhook
API
endpoint
JSON
JWT
CUDA
NVIDIA
NVDA

8. NO inventar información.

Esta regla es crítica.

El modelo puede:

- limpiar
- estructurar
- corregir
- interpretar autocorrecciones
- aplicar formato solicitado

Pero NO debe agregar ideas o información que el usuario no haya dicho.

Ante ambigüedad, debe ser conservador y mantener el contenido original en vez de inventar.

MODOS

Quiero estudiar la posibilidad de tener varios modos/hotkeys.

Como mínimo:

MODO INTELIGENTE

Whisper
-> formatter
-> Ollama
-> insertar

MODO LITERAL

Whisper
-> formatter
-> insertar

Sin Ollama.

MODO TRADUCCIÓN

Hablar en español y producir directamente texto natural en inglés.

Idealmente también permitir posteriormente:

inglés -> español

La traducción debe conservar intención, tono, nombres propios y términos técnicos.

No traduzcas nombres de productos, APIs o términos que no corresponda traducir.

HOTKEYS

Actualmente F8 funciona correctamente como push-to-talk.

Propón una distribución de hotkeys para los diferentes modos antes de implementarla.

Evita combinaciones problemáticas de Windows.

Las hotkeys deben ser configurables mediante config.json.

No dependas exclusivamente de la GUI.

OLLAMA

Ollama ya está instalado localmente.

Diseña la integración de manera desacoplada.

Quiero algo parecido a:

TextProcessor interface/protocol
    |
    +-- PassthroughProcessor
    |
    +-- OllamaProcessor
    |
    +-- TranslationProcessor o modos equivalentes

No es obligatorio usar exactamente esos nombres.

El objetivo es evitar acoplar toda la aplicación directamente a Ollama.

REQUISITOS IMPORTANTES PARA OLLAMA

1. Timeout configurable.

2. Si Ollama está apagado o falla:

NO perder la transcripción.

Debe hacer fallback al texto procesado por el formatter y pegarlo normalmente.

3. Registrar el error en logs.

4. No bloquear indefinidamente la aplicación.

5. Permitir configurar:

- URL de Ollama
- modelo
- timeout
- modo inteligente habilitado/deshabilitado

6. Preferentemente usar HTTP directamente contra la API local de Ollama si eso evita dependencias innecesarias.

7. Evaluar streaming sólo si aporta una ventaja real. Para dictados cortos probablemente no sea necesario.

LATENCIA

La experiencia debe seguir sintiéndose como dictado.

No quiero esperar muchos segundos después de cada frase.

Mide por separado:

- duración del audio
- tiempo de transcripción
- tiempo del procesamiento inteligente
- tiempo total

Añade esos datos al logging cuando sea apropiado.

PROMPT DEL MODELO

El prompt debe estar diseñado específicamente para dictado.

No quiero un chatbot.

El modelo debe devolver SOLAMENTE el texto final que se va a insertar.

No debe responder cosas como:

"Claro, aquí tienes el texto corregido:"

No debe usar Markdown salvo que el usuario haya solicitado una estructura donde Markdown/texto estructurado tenga sentido, como listas.

No debe explicar lo que hizo.

No debe contestar preguntas contenidas en el dictado.

Ejemplo:

Si dicto:

"¿A qué hora vamos a hacer el deploy?"

Debe insertar:

"¿A qué hora vamos a hacer el deploy?"

NO debe responder a la pregunta.

Esto es extremadamente importante.

TRADUCCIÓN

Agregar un modo específico de traducción.

Ejemplo hablado:

"Hola John, ya terminamos las pruebas de Mercado Pago. Mañana podemos revisar los resultados."

Salida en inglés:

"Hi John, we've finished the Mercado Pago tests. We can review the results tomorrow."

El modelo no debe contestar el mensaje; solamente traducirlo/adaptarlo de manera natural.

ACCESIBILIDAD

El usuario principal utiliza NVDA y es ciego/low-vision.

La aplicación debe poder utilizarse completamente mediante teclado y lector de pantalla.

La GUI actual de Settings tiene problemas de accesibilidad.

Por lo tanto:

1. Toda nueva configuración debe poder establecerse también mediante config.json.

2. No hagas que una funcionalidad importante dependa exclusivamente de controles gráficos.

3. Los elementos de menú de la bandeja deben tener etiquetas textuales claras.

4. Evitar controles personalizados inaccesibles cuando sea posible.

5. Si modificas Settings, utiliza controles estándar compatibles con teclado y lectores de pantalla.

6. El foco mediante teclado debe ser predecible.

7. No dependas de color, iconos o posición visual para comunicar estado.

8. Los estados importantes deben estar disponibles como texto accesible.

CONFIGURACIÓN

Mantener compatibilidad hacia atrás.

Si faltan las nuevas propiedades en config.json, deben utilizarse defaults seguros.

Una configuración vieja no debe provocar errores.

Idealmente considerar propiedades como:

smart_processing
ollama_url
ollama_model
ollama_timeout
translation_target_language

Los nombres definitivos los puedes proponer tú.

VOCABULARIO

Whispr ya tiene dictionary/replacements.

Conserva esa funcionalidad.

Analiza cómo debería interactuar con el procesamiento inteligente.

El vocabulario técnico/personalizado no debería perder su capitalización después de pasar por Ollama.

PRIVACIDAD

Todo debe permanecer local.

No agregar:

- telemetría
- analytics
- APIs cloud
- servicios externos

No enviar audio ni texto fuera del equipo.

TESTS

Quiero tests para la nueva funcionalidad.

Como mínimo:

1. Formatter existente.
2. Comandos hablados en inglés.
3. Comandos hablados en español.
4. Configuración vieja sin nuevas propiedades.
5. Fallback cuando Ollama no responde.
6. Timeout de Ollama.
7. Processor passthrough.
8. Parsing seguro de la respuesta de Ollama.
9. No perder transcripción ante error.
10. Traducción mediante processor mock.
11. Autocorrección mediante processor mock.
12. Listas mediante processor mock.

No quiero que los tests normales requieran tener Ollama ejecutándose.

Usa mocks/fakes para la integración.

Puedes agregar opcionalmente integration tests separados para Ollama.

LOGGING

Nunca registrar información sensible innecesariamente.

Permitir diagnosticar:

- modelo Whisper
- dispositivo
- tiempo de transcripción
- processor utilizado
- tiempo de procesamiento
- fallback
- errores

Evalúa si conviene NO guardar el contenido completo de los dictados en logs por privacidad.

ROBUSTEZ

El dictado literal debe seguir funcionando aunque:

- Ollama no esté instalado
- Ollama esté apagado
- el modelo no exista
- haya timeout
- Ollama devuelva error
- Ollama devuelva una respuesta vacía

En cualquiera de esos casos:

usar la transcripción original/formateada.

Nunca perder el dictado.

NO CAMBIAR SIN NECESIDAD

No reemplazar:

- faster-whisper
- sistema de captura de audio
- sistema actual de inyección
- CUDA
- tray icon
- configuración existente

salvo que encuentres una razón técnica importante y la expliques primero.

No introducir frameworks grandes innecesariamente.

PROCESO DE TRABAJO QUE QUIERO

FASE 1

Analiza el proyecto y los cambios locales.

No modifiques nada todavía.

Entrega:

- arquitectura actual
- puntos de integración
- riesgos
- propuesta de arquitectura
- propuesta de hotkeys
- modelo Ollama recomendado para mi hardware
- estimación de latencia
- archivos que sería necesario modificar/agregar
- estrategia de tests

FASE 2

Después de mi aprobación:

Implementar la infraestructura de processors y configuración sin cambiar todavía el comportamiento por defecto.

FASE 3

Agregar Ollama Smart Dictation.

FASE 4

Agregar traducción.

FASE 5

Mejorar accesibilidad/configuración si resulta necesario.

FASE 6

Tests, documentación y limpieza.

HARDWARE

Equipo:

Lenovo LOQ
32 GB RAM
NVIDIA RTX 5060 Laptop
8 GB VRAM
Windows 11 Pro

Whisper large-v3-turbo ya funciona acelerado por CUDA.

IMPORTANTE SOBRE RECURSOS

Whisper y Ollama pueden competir por VRAM.

Antes de elegir el modelo Ollama:

- considera los 8 GB de VRAM disponibles
- considera que faster-whisper está usando GPU
- mide VRAM durante el uso
- evita provocar OOM
- considera modelos pequeños/rápidos cuantizados
- considera si conviene mantener ambos modelos cargados simultáneamente

Actualmente también tengo algunos modelos instalados en Ollama, pero no asumas que necesariamente son los adecuados. Inspecciona los modelos disponibles antes de recomendar uno.

CRITERIO PRINCIPAL

Prefiero:

fiabilidad + baja latencia + privacidad + accesibilidad

por encima de una arquitectura excesivamente sofisticada.

La experiencia final debería sentirse así:

mantengo una hotkey
-> hablo naturalmente
-> suelto la hotkey
-> aparece rápidamente un texto limpio, correctamente estructurado y fiel a lo que quise decir.

Empieza ÚNICAMENTE con la FASE 1.

No modifiques archivos todavía.