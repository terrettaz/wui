/*
 * Javascript library based on Prototypejs framework which provide
 * AutoComplete and Token classes with Ajax calls to update views
 *  
 * Author: Pierrick Terrettaz <pierrick a.t. gmail.com>
 * Last modified: 2008/10/06
 * Version: 1.1
 * Apache License Version 2.0
 * http://www.apache.org/licenses/LICENSE-2.0.txt
 *----------------------------------------------------------------*/
 
/**
 * WUI namespace
 * @namespace WUI
 * Contains:
 *  - @class AutoComplete
 *  - @class Token
 */
var WUI = {
    prefixId: 'wuiid_'
}

/**
 * AutoComplete javascript class which reacts with keyring on input field
 * and display the result to help end-user to choose on diffrents items.
 * @class AutoComplete
 * @notice Protocol
 *     The ajax response must be a JSON content with content-type
 *     'application/json'
 *     Content response must be a list of object. Each objects must
 *     contains at least 'id', 'label fields. All extra field are
 *     optional but can be used by AutoComplete.options.rowTemplate
 *     JSON:
 *     [ {"id":1,"label":"lable1"},{"id":2,"label":"lable2"} ]
 */
WUI.AutoComplete = Class.create({
    
    input: null,
    result: null,
    selected: null,
    searchCounter: 0,
    mouseoverResult: false,
    
    /**
     * Constructor
     * @parameter input: HTML Input id of the base input
     * @options 
     *  - data:    (Array) array of objects (id,label,selected) to be searched
     *  - dataUrl: (String) url which provides search result as json
     *  - rowTemplate: (prototypejs:Template) for the rendering
     *                 of each results
     *                 example: new Template('<div>#{label}</div>')
     */
    initialize: function(input, options) {
        this.input = $(input);
        this.options = {
            data: new Array(),
            dataUrl: null,
            rowTemplate: new Template('<span>#{label}</span>'),
        };
        Object.extend(this.options, options || { });
        
        if (this.input.tagName.toLowerCase() != 'input' || this.input.type != 'text') {
            throw Exception('LiveSerch can be only added to an input#text');
        }
        
        this.result = new Element('div', {'class': 'liveSearchResult'}).hide();
        
        this.result.observe('mouseover', (function(event){
            if (!this.mouseoverResult)
                this.mouseoverResult = true;
        }).bind(this))
        .observe('mouseout', (function(event){
            if (this.mouseoverResult)
                this.mouseoverResult = false;
        }).bind(this));
        
        this.input.insert({after:this.result});
        this.input.observe('keyup', this.liveSearch.bind(this));
        if (/Konqueror|Safari/.test(navigator.userAgent)) {
            this.input.observe('keydown', this.moveSelection.bind(this));
        } else {
            this.input.observe('keypress', this.moveSelection.bind(this));
        }
        this.input.observe('blur', (function(event) {
            if (!this.mouseoverResult)
                this.result.hide();
        }).bind(this));
        this.input.observe('focus', (function(event) {
            this.liveSearch(event);
        }).bind(this));
        
        // to avoid autosumission of form when return is pressed
        this.input.onkeypress = function(event) {
            if (event.keyCode == 13)
                return false;
        };
    },
    
    moveSelection: function(event){
        switch (event.keyCode) {
            
            case 13:
                this.handleSelectedItem();
                return false;
                break;
            
            case 38:
                if (this.selected == null)
                    break;
            
                this.selected.removeClassName('selected');
                this.selected = this.selected.previous();
                if (this.selected != null) {
                    this.selected.addClassName('selected');
                    this.selected.scrollTo();
                }
                break;
        
            case 40:
                var container = this.result;
                if (container.childElements().length > 0 && !container.childElements()[0].hasClassName('empty')) {
                    if (this.selected == null) {
                        this.selected = container.childElements()[0];
                    }    
                    else {
                        this.selected.removeClassName('selected');
                        if (this.selected.next() != null)
                            this.selected = this.selected.next();
                    }
                    this.selected.addClassName('selected');
                }
                break;        
        }
        
        if (this.selected != null) {
            var y = this.selected.y ? this.selected.y : this.selected.offsetTop;
            this.result.scrollTop=y-(this.result.getHeight() - this.selected.getHeight());
        }
    },
    
    liveSearch: function(event){
        switch (event.keyCode) {
            case 13:
            case 38:
            case 40:
                break;
        
            default:
                this.selected = null;
            
                if (event.target.value == '') {
                    this.result.update(new Element('div', {'class':'empty'}).update('start typing ...'));
                    return;
                }
            
                this.result.update(new Element('div', {'class':'empty'}).update('searching ...'));
                this.selectedId = null;
                if (!this.result.visible())
                    this.result.show();
                this.doSearch.bind(this).delay(0.6, ++this.searchCounter);
        }
    },
    
    doSearch: function(id) {
        if (id != this.searchCounter)
            return;
        
        if (this.options.dataUrl != null) {
            if (this.options.dataUrl.include('?'))
                var url = this.options.dataUrl + '&s='+this.input.value;
            else
                var url = this.options.dataUrl + '?s='+this.input.value;
            new Ajax.Request(url, {
                onSuccess: (function(trans) {
                    this.handleResults.bind(this);
                    this.handleResults(trans.responseJSON);
                }).bind(this),
                onComplete: (function(trans) {
                    
                }).bind(this),
                onFailure: (function(trans) {
                    this.result.update(new Element('div', {'class':'empty'}).update('error while loading :('));
                }).bind(this)
            });
        } else {
            var results = new Array();
            this.options.data.each((function(item){
                if (item.label.toLowerCase().startsWith(this.input.value.toLowerCase()))
                    results.push(Object.clone(item));
            }).bind(this));
            
            this.handleResults.bind(this);
            this.handleResults(results);
        }
    },
    
    handleResults: function(items) {
        var reg = new RegExp("("+this.input.value+")", "gi");
        this.result.update('');
        if (items.length > 0)
            this.result.show();
        else
            this.result.update(new Element('div', {'class':'empty'}).update('nothing found'));

        items.each((function(item, index){
            if (index % 2 == 0)
                odd = 'odd';
            else
                odd = 'even';
            
            item.label = item.label.replace(reg,'<span class="highlight">$1</span>');
            
            var el = new Element('div', {'id': WUI.prefixId+item.id, 'class':odd})
                .update(this.options.rowTemplate.evaluate(item))
                .observe('mouseover', (function(event){
                    el.addClassName('selected');
                    this.selected = this;
                }).bind(this))
                .observe('mouseout', (function(event){
                    this.result.childElements().each(function (element, index){
                        element.removeClassName('selected');
                    });
                    this.selected = null;
                }).bind(this))
                .observe('click', (function(event){
                    this.selected = el;
                    this.handleSelectedItem();
                }).bind(this));
            el.item = item;
            this.result.insert(el);
            
        }).bind(this));
    },
    
    handleSelectedItem: function() {
        if (this.selected != null) {
            this.input.value = this.selected.innerHTML.replace(/(<([^>]+)>)/ig,"");
            this.result.hide();
            this.selected = null;
        }
    },
    
    clear: function() {
        this.input.value = '';
    },
    
});

/**
 * Token javascript class which creates tokens based on end-user search results
 * Can be used like html select tag with single or multiple values
 * @class Token
 * @super AutoComplete
 * @notice Protocol
 *     The ajax response must be a JSON content with content-type
 *     'application/json'
 *     Content response must be a list of object. Each objects must
 *     contains at least 'id', 'label fields. All extra field are
 *     optional but can be used by Token.options.rowTemplate
 *     JSON:
 *     [ {"id":1,"label":"lable1"},{"id":2,"label":"lable2"} ]
 */
WUI.Token = Class.create(WUI.AutoComplete, {

    fakeInput: null,
    inputName: null,
    stop: null,
    
    /**
     * Constructor
     * @parameter input: HTML Input id of the base input
     * @options 
     *  - data:     (Array) array of objects (id,label,selected) to be searched
     *  - dataUrl:  (String) url which provides search result as json
     *  - selected: (Array) array of id to init the token
     *  - rowTemplate: (prototypejs:Template) for the rendering
     *                 of each results
     *                 example: new Template('<div>#{label}</div>')
     *  - multiple: (Boolean) allow multiple selection.
     *              Aka <select multiple="multiple"> (default: true)
     */
    initialize: function ($super, input, options) {
        $super(input, options);

        this.options = Object.extend({
            multiple: true,
            selected: new Array(),
            onAdd: function(event){},
            onRemove: function(event){},
        }, this.options);
        
        this.inputName = this.input.name;
        this.input.setAttribute('name', this.inputName + '_text');
        this.fakeInput = new Element('div', {'class': 'fakeInput'});
        this.fakeInput.observe('click', (function(event){
            this.focus();
        }).bind(this.input));
        var parent = this.input.up();
        parent.insert({bottom:this.fakeInput});
        parent.insert({bottom:this.result.remove()});
        parent.insert({bottom:this.container});
        this.stop = new Element('span', {'class':'stop'});
        this.fakeInput.insert(this.stop);
        this.fakeInput.insert(new Element('div', {'class':'tokenizer'}).update(this.input.remove()));
        this.fakeInput.insert(new Element('div').setStyle({'clear':'both'}));
        //this.input.setStyle({padding: 0, margin: 0, border: 0}).focus();
        this.input.observe('keydown', this.onKeypress.bind(this));
        this.input.observe('dblclick', this.onDblclick.bind(this));
        
        this.options.data.each((function(item) {
            if (item.selected || this.options.selected.grep('^'+item.id+'$').length > 0) {
                this.stop.insert({before: this.createToken(item.id, item.label)});
            }
        }).bind(this));
    },
    
    getIds: function() {
        var ids = new Array();
        var tokens = this.fakeInput.select('.token');
        tokens.each(function(token){
            ids.push(token.down('input').value);
        });
        return ids;
    },
    
    onDblclick: function(event) {
        this.fakeInput.select('.token').invoke('addClassName', 'token_selected');
    },
    
    onKeypress: function(event) {
        if (event.keyCode == 8  && this.input.value.length == 0) {    
            var token = this.stop.previous('.token');
            if (token != null && !token.hasClassName('token_selected')) {
                token.addClassName('token_selected');
            } else if (event.keyCode == 8){
                var tokens = this.fakeInput.select('.token_selected');
                tokens.each(function(token){
                    token.remove();
                    token.fire('token:remove');
                });
            }
        } else {
            var tokens = this.fakeInput.select('.token_selected');
            tokens.each(function(token){
                token.removeClassName('token_selected');
            });
        }
    },
    
    handleSelectedItem: function() {
        if (this.selected != null) {
            var id = this.selected.id.substring(WUI.prefixId.length);
            var label= this.selected.innerHTML.replace(/(<([^>]+)>)/ig,"");
            label = this.selected.item.label.replace(/(<([^>]+)>)/ig,"");
            if (!this.options.multiple) {
                var token = this.stop.previous('.token');
                if (token != null) {
                    token.remove();
                }
            }
            var token = this.createToken(id, label);
            this.stop.insert({before: token});
            this.input.value = '';
            this.result.hide();
            this.selected = null;
            token.fire('token:add');
        }
    },
    
    clear: function() {
        this.input.value = '';
        var tokens = this.fakeInput.select('.token');
        tokens.each(function(token){
            token.remove();
            token.fire('token:remove');
        });
    },
    
    createToken: function(id, label) {
        var labelContainer = new Element('span', {'class':'label'}).insert(label);
        var inputHidden = new Element('input', {'type':'hidden', 'name':this.inputName, 'value':id});
        var token = new Element('span', {'class':'token'}).insert(
            new Element('span').insert(
                new Element('span').insert(
                    new Element('span').insert(
                        new Element('span').insert(
                            inputHidden).insert(
                                labelContainer)))));
        
        token.observe('token:remove', this.options.onRemove.bind(this, token.down('input').value));
        token.observe('token:add', this.options.onAdd.bind(this, token.down('input').value));
        var removeButton = new Element('div', {'class':'token_remove'}).update('&nbsp;');
        removeButton.token = token;
        removeButton.observe('click', (function(event){
            this.token.remove();
            this.token.fire('token:remove');
        }));
        labelContainer.insert({top:removeButton});
        return token;
    }
});