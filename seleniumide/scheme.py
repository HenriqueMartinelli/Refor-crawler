# Dictionary with the description of the site screens,
# each screen has an indication of screen iframe, available actions and elements for interaction
SITE_SCHEME = {
    "Login": {
        "iframe": "WA1",
        "actions": ["login"],
        "elements": {
            "usernameInput": "//input[@data-testtoolid='idusuario']",
            "passwordInput": "//input[@data-testtoolid='senha']",
            "enterButton": "//button[@data-testtoolid='onclickenviar']"
        }
    },
    "Home": {
        "iframe": "WA2",
        "actions": ["navigate_to_practical_exam_schedule"],
        "elements": {
            "name": "//input[@data-testtoolid='mostrausuario']",
            "praticalExamSchedule": "//a[@title='AGENDAMENTO DE EXAME PRÁTICO']",
            "praticalExamScheduleRequest": "//a[@title='Pedido de Agendamento']",
            "btnLogout": "//span[@id='$8']",
            "verifyPraticalExame": "//a[@title='Cancelamento de Agendamento']"
        }
    },
    "PraticalExamScheduleRequest": {
        "iframe": "WA0",
        "actions": ["get_pratical_exam_categories", "set_pratical_exam_category", "solve_captcha"],
        "elements": {
            "categorySelect": "//select[@data-testtoolid='w_categoria']",
            "captchaInput": "//input[@data-testtoolid='w_texto_captcha']",
            "captchaImage": "//img[@data-testtoolid='img_IO_44']",
            "captchaReloadButton": "//a[@id='MLINK41']",
            "btnLogout": "//span[@id='$8']",
            "captchaSendButton": "//button[@data-testtoolid='onclickselecionar']",
        }
    },
    "PraticalExamScheduleRequestForm": {
        "iframe": "WA1",
        "actions": ["get_schedule_grid_options", "set_schedule_grid_option",
                    "get_pratical_exam_vehicles", "set_pratical_exam_vehicle",
                    "set_renach", "solve_captcha"],
        "elements": {
            "dateOptionSelect": "//select[@data-testtoolid='w_dtgradeagenda']",
            "vehicleOptionSelect": "//select[@data-testtoolid='w_veic1']",
            "renachInput1": "//input[@data-testtoolid='w_renach1']",
            "captchaInput": "//input[@data-testtoolid='w_texto_captcha']",
            "captchaImage": "//img[@data-testtoolid='img_IO_95']",
            "captchaReloadButton": "//a[@data-testtoolid='onClickexibir']",
            "captchaSendButton": "//button[@data-testtoolid='onclick_agendar']",
            "btnVoltar": "//button[@data-testtoolid='onClickBtnVoltar']",
            "btnLogout": "//span[@id='$8']",
            "inputResult": "//input[@data-testtoolid='w_agendamento_ok1']"

        }
    },
    "VerifyPraticalExam": {
    "iframe": "WA0",
        "actions": ["get_pratical_exam_categories", "set_pratical_exam_category", "solve_captcha"],
        "elements": {
            "categorySelect": "//select[@data-testtoolid='w_categoria_AB']",
            "renachInput1": "//input[@data-testtoolid='w_formulario_renach']",
            "verifyButton": "//button[@data-testtoolid='onClickEnviar']",
            "btnLogout": "//span[@id='$8']",

            "cancelButton": "//button[@data-testtoolid='onClickConfirmar']"
        }
    },

    "PraticalExamScheduleRequestResult": {
    "iframe": "WA1",
        "actions": ["get_pratical_exam_categories", "set_pratical_exam_category", "solve_captcha"],
        "elements": {
            "inputResult": "//input[@data-testtoolid='w_agendamento_ok1']",
            "renachInput1": "//input[@data-testtoolid='w_formulario_renach']",
            "verifyButton": "//button[@data-testtoolid='onClickEnviar']",
            "btnLogout": "//span[@id='$8']",
            "cancelButton": "//button[@data-testtoolid='onClickConfirmar']"
        }
    }
    
}
