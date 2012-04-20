define [
  'chaplin/view', 'text!templates/home.hbs'
], (View, template) ->

  class IndexView extends View

    autoRender: true
    containerSelector: '#content'
    id: 'home'
    @template: template

