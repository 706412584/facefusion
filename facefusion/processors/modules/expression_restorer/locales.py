from facefusion.types import Locales

LOCALES : Locales =\
{
	'en':
	{
		'help':
		{
			'model': 'choose the model responsible for restoring the expression',
			'factor': 'restore factor of expression from the target face',
			'areas': 'choose the items used for the expression areas (choices: {choices})'
		},
		'uis':
		{
			'model_dropdown': 'EXPRESSION RESTORER MODEL',
			'factor_slider': 'EXPRESSION RESTORER FACTOR',
			'areas_checkbox_group': 'EXPRESSION RESTORER AREAS'
		}
	},
	'zh':
	{
		'help':
		{
			'model': '选择负责表情恢复的模型',
			'factor': '从目标人脸恢复表情的因子',
			'areas': '选择用于表情区域的项目（选项：{choices}）'
		},
		'uis':
		{
			'model_dropdown': '表情恢复模型',
			'factor_slider': '表情恢复因子',
			'areas_checkbox_group': '表情恢复区域'
		}
	}
}
