extends Control

@onready var toggle_button := $Button
var is_on := false

func _ready():
	toggle_button.text = "OFF"
	toggle_button.pressed.connect(_on_button_pressed)

func _on_button_pressed():
	is_on = !is_on
	toggle_button.text = "ON" if is_on else "OFF"

	var message = "LED_ON" if is_on else "LED_OFF"
	WsServer.broadcast(message)

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass
