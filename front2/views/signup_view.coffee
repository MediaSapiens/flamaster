define [
  'chaplin/view',
  'text!templates/sign_up.hbs'
], (View, template) ->
  'use strict'

  class SignUpView extends View

    autoRender: true
    containerSelector: "#content"
    id: "signup"
    @template = template

    getTemplateData: ->
      data =
        form:
          id: 'sigup-form'
          method: 'post'
          action: '.'
      data
