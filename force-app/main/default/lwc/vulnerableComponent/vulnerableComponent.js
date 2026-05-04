import { LightningElement } from 'lwc';

export default class VulnerableComponent extends LightningElement {
    userInput = '';

    handleInput(event) {
        this.userInput = event.target.value;
    }

    get unsafeHtml() {
        // Vulnerable to XSS
        return '<div>' + this.userInput + '</div>';
    }
}