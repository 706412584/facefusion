from facefusion.types import Locales

LOCALES : Locales =\
{
	'en':
	{
		'help':
		{
			'model': 'choose the model responsible for removing the background',
			'fill_color': 'apply red, green, blue and alpha values to the background',
			'despill_color': 'remove red, green, blue and alpha values from the foreground'
		},
		'uis':
		{
			'model_dropdown': 'BACKGROUND REMOVER MODEL',
			'fill_color_red_number': 'FILL COLOR RED',
			'fill_color_green_number': 'FILL COLOR GREEN',
			'fill_color_blue_number': 'FILL COLOR BLUE',
			'fill_color_alpha_number': 'FILL COLOR ALPHA',
			'despill_color_red_number': 'DESPILL COLOR RED',
			'despill_color_green_number': 'DESPILL COLOR GREEN',
			'despill_color_blue_number': 'DESPILL COLOR BLUE',
			'despill_color_alpha_number': 'DESPILL COLOR ALPHA'
		}
	},
	'zh':
	{
		'help':
		{
			'model': '选择负责移除背景的模型',
			'fill_color': '对背景应用红、绿、蓝和透明度值',
			'despill_color': '从前景移除红、绿、蓝和透明度值'
		},
		'uis':
		{
			'model_dropdown': '背景移除模型',
			'fill_color_red_number': '填充颜色红',
			'fill_color_green_number': '填充颜色绿',
			'fill_color_blue_number': '填充颜色蓝',
			'fill_color_alpha_number': '填充颜色透明度',
			'despill_color_red_number': '去溢色红',
			'despill_color_green_number': '去溢色绿',
			'despill_color_blue_number': '去溢色蓝',
			'despill_color_alpha_number': '去溢色透明度'
		}
	}
}
