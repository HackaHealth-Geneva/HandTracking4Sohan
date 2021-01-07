using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RightChoice_SceneManager : MonoBehaviour
{

    public GameObject Audio; 
    // Start is called before the first frame update
    void Start()
    {
        GameManager.NumberOfplays++; 
        GameManager.difficultyLevel++;

        
        GameManager.SelectedGO.transform.position=  new Vector3(0,0,0);

        GameManager.SelectedGO.GetComponent<Animator>().SetBool("ToWin", true);
        GameManager.SelectedGO.GetComponent<Animator>().SetBool("ToCalling", false);
        GameManager.SelectedGO.GetComponent<Animator>().SetBool("ToIdle", false);




        Invoke("PlayAudio", 1.0f);
        Invoke("PlayAgain", 5.0f);
    }

    void PlayAudio()
    {
        Audio.GetComponent<AudioSource>().Play();
    }

    void PlayAgain()
    {
        GameManager.Instance.LoadInitialScene();

    }

    // Update is called once per frame
    void Update()
    {
    }
}
