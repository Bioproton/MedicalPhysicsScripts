*$ CREATE MGDRAW.FOR
*COPY MGDRAW
*                                                                      *
*=== mgdraw ===========================================================*
*                                                                      *
      SUBROUTINE MGDRAW ( ICODE, MREG )

      INCLUDE '(DBLPRC)'
      INCLUDE '(DIMPAR)'
      INCLUDE '(IOUNIT)'
*
*----------------------------------------------------------------------*
*                                                                      *
*     Copyright (C) 1990-2013      by        Alfredo Ferrari           *
*     All Rights Reserved.                                             *
*                                                                      *
*                                                                      *
*     MaGnetic field trajectory DRAWing: actually this entry manages   *
*                                        all trajectory dumping for    *
*                                        drawing                       *
*                                                                      *
*     Created on   01 March 1990   by        Alfredo Ferrari           *
*                                              INFN - Milan            *
*     Last change   12-Nov-13      by        Alfredo Ferrari           *
*                                              INFN - Milan            *
*                                                                      *
*----------------------------------------------------------------------*
*
      INCLUDE '(CASLIM)'
      INCLUDE '(COMPUT)'
      INCLUDE '(SOURCM)'
      INCLUDE '(FHEAVY)'
      INCLUDE '(FLKSTK)'
      INCLUDE '(GENSTK)'
      INCLUDE '(MGDDCM)'
      INCLUDE '(PAPROP)'
      INCLUDE '(QUEMGD)'
      INCLUDE '(SUMCOU)'
      INCLUDE '(TRACKR)'
      INCLUDE '(RESNUC)' 
      INCLUDE '(EVTFLG)'

      INTEGER ONCASE,OJTRACK,OICODE,OOICODE,oiona,oionz,oaa,ozz
* RESNUC added by Anna
* testing   
*
      DIMENSION DTQUEN ( MXTRCK, MAXQMG )
*
      CHARACTER*20 FILNAM
      LOGICAL LFCOPE
      SAVE LFCOPE
      DATA LFCOPE / .FALSE. /
*
*----------------------------------------------------------------------*
*                                                                      *
*     Icode = 1: call from Kaskad                                      *
*     Icode = 2: call from Emfsco                                      *
*     Icode = 3: call from Kasneu                                      *
*     Icode = 4: call from Kashea                                      *
*     Icode = 5: call from Kasoph                                      *
*                                                                      *
*----------------------------------------------------------------------*
*                                                                      *
      IF ( .NOT. LFCOPE ) THEN
         LFCOPE = .TRUE.
         IF ( KOMPUT .EQ. 2 ) THEN
            FILNAM = '/'//CFDRAW(1:8)//' DUMP A'
         ELSE
            FILNAM = CFDRAW
         END IF
         OPEN ( UNIT = IODRAW, FILE = FILNAM, STATUS = 'NEW', FORM =
     &          'UNFORMATTED' )
      END IF
*  +-------------------------------------------------------------------*
*  |  Quenching is activated
      IF ( LQEMGD ) THEN
         IF ( MTRACK .GT. 0 ) THEN
            RULLL  = ZERZER
            CALL QUENMG ( ICODE, MREG, RULLL, DTQUEN )
*            WRITE (IODRAW) ( ( SNGL (DTQUEN (I,JBK)), I = 1, MTRACK ),
*     &                         JBK = 1, NQEMGD )
         END IF
      END IF
*  |  End of quenching
*     +-------------------------------------------------------------------*
      RETURN
*
*======================================================================*
*                                                                      *
*     Boundary-(X)crossing DRAWing:                                    *
*                                                                      *
*     Icode = 1x: call from Kaskad                                     *
*             19: boundary crossing                                    *
*     Icode = 2x: call from Emfsco                                     *
*             29: boundary crossing                                    *
*     Icode = 3x: call from Kasneu                                     *
*             39: boundary crossing                                    *
*     Icode = 4x: call from Kashea                                     *
*             49: boundary crossing                                    *
*     Icode = 5x: call from Kasoph                                     *
*             59: boundary crossing                                    *
*                                                                      *
*======================================================================*
*
      ENTRY BXDRAW ( ICODE, MREG, NEWREG, XSCO, YSCO, ZSCO )
      RETURN
****************END OF CODE BY ANNA****************************
*
*======================================================================*
*                                                                      *
*     Event End DRAWing:                                               *
*                                                                      *
*======================================================================*
*                                                                      *
      ENTRY EEDRAW ( ICODE )
      RETURN
*
*======================================================================*
*                                                                      *
*     ENergy deposition DRAWing:                                       *
*                                                                      *
*     Icode = 1x: call from Kaskad                                     *
*             10: elastic interaction recoil                           *
*             11: inelastic interaction recoil                         *
*             12: stopping particle                                    *
*             13: pseudo-neutron deposition                            *
*             14: escape                                               *
*             15: time kill                                            *
*     Icode = 2x: call from Emfsco                                     *
*             20: local energy deposition (i.e. photoelectric)         *
*             21: below threshold, iarg=1                              *
*             22: below threshold, iarg=2                              *
*             23: escape                                               *
*             24: time kill                                            *
*     Icode = 3x: call from Kasneu                                     *
*             30: target recoil                                        *
*             31: below threshold                                      *
*             32: escape                                               *
*             33: time kill                                            *
*     Icode = 4x: call from Kashea                                     *
*             40: escape                                               *
*             41: time kill                                            *
*             42: delta ray stack overflow                             *
*     Icode = 5x: call from Kasoph                                     *
*             50: optical photon absorption                            *
*             51: escape                                               *
*             52: time kill                                            *
*                                                                      *
*======================================================================*
*                                                                      *
      ENTRY ENDRAW ( ICODE, MREG, RULL, XSCO, YSCO, ZSCO )
      IF ( .NOT. LFCOPE ) THEN
         LFCOPE = .TRUE.
         IF ( KOMPUT .EQ. 2 ) THEN
            FILNAM = '/'//CFDRAW(1:8)//' DUMP A'
         ELSE
            FILNAM = CFDRAW
         END IF
         OPEN ( UNIT = IODRAW, FILE = FILNAM, STATUS = 'NEW', FORM =
     &          'UNFORMATTED' )
      END IF
*      WRITE (IODRAW)  0, ICODE, JTRACK, SNGL (ETRACK), SNGL (WTRACK)
*      WRITE (IODRAW)  SNGL (XSCO), SNGL (YSCO), SNGL (ZSCO), SNGL (RULL)
*  +-------------------------------------------------------------------*
*  |  Quenching is activated : calculate quenching factor
*  |  and store quenched energy in DTQUEN(1, jbk)
      IF ( LQEMGD ) THEN
         RULLL = RULL
         CALL QUENMG ( ICODE, MREG, RULLL, DTQUEN )
*         WRITE (IODRAW) ( SNGL (DTQUEN(1, JBK)), JBK = 1, NQEMGD )
      END IF
*  |  end quenching
*  +-------------------------------------------------------------------*
      RETURN
*
*======================================================================*
*                                                                      *
*     SOurce particle DRAWing:                                         *
*                                                                      *
*======================================================================*
*
      ENTRY SODRAW
      IF ( .NOT. LFCOPE ) THEN

      END IF
*      WRITE (IODRAW) -NCASE, NPFLKA, NSTMAX, SNGL (TKESUM),
*     &                SNGL (WEIPRI)
*  +-------------------------------------------------------------------*
*  |  (Radioactive) isotope: it works only for 1 source particle on
*  |  the stack for the time being
      IF ( ILOFLK (NPFLKA) .GE. 100000 .AND. LRADDC (NPFLKA) ) THEN
         IARES  = MOD ( ILOFLK (NPFLKA), 100000  )  / 100
         IZRES  = MOD ( ILOFLK (NPFLKA), 10000000 ) / 100000
         IISRES = ILOFLK (NPFLKA) / 10000000
         IONID  = ILOFLK (NPFLKA)
*         WRITE (IODRAW) ( IONID,SNGL(-TKEFLK(I)),
*     &                    SNGL (WTFLK(I)), SNGL (XFLK (I)),
*     &                    SNGL (YFLK (I)), SNGL (ZFLK (I)),
*     &                    SNGL (TXFLK(I)), SNGL (TYFLK(I)),
*     &                    SNGL (TZFLK(I)), I = 1, NPFLKA )
*  |
*  +-------------------------------------------------------------------*
*  |  Patch for heavy ions: it works only for 1 source particle on
*  |  the stack for the time being
      ELSE IF ( ABS (ILOFLK (NPFLKA)) .GE. 10000 ) THEN
         IONID = ILOFLK (NPFLKA)
         CALL DCDION ( IONID )
*  |
*  +-------------------------------------------------------------------*
*  |  Patch for heavy ions: ???
      ELSE IF ( ILOFLK (NPFLKA) .LT. -6 ) THEN
*         WRITE (IODRAW) ( IONID,SNGL(TKEFLK(I)+AMNHEA(-ILOFLK(NPFLKA))),
*     &                    SNGL (WTFLK(I)), SNGL (XFLK (I)),
*     &                    SNGL (YFLK (I)), SNGL (ZFLK (I)),
*     &                    SNGL (TXFLK(I)), SNGL (TYFLK(I)),
*     &                    SNGL (TZFLK(I)), I = 1, NPFLKA )
*  |
*  +-------------------------------------------------------------------*
*  |
      ELSE
*         WRITE (IODRAW) ( ILOFLK(I), SNGL (TKEFLK(I)+AM(ILOFLK(I))),
*     &                    SNGL (WTFLK(I)), SNGL (XFLK (I)),
*     &                    SNGL (YFLK (I)), SNGL (ZFLK (I)),
*     &                    SNGL (TXFLK(I)), SNGL (TYFLK(I)),
*     &                    SNGL (TZFLK(I)), I = 1, NPFLKA )
      END IF
*  |
*  +-------------------------------------------------------------------*
      RETURN
*
*======================================================================*
*                                                                      *
*     USer dependent DRAWing:                                          *
*                                                                      *
*     Icode = 10x: call from Kaskad                                    *
*             100: elastic   interaction secondaries                   *
*             101: inelastic interaction secondaries                   *
*             102: particle decay  secondaries                         *
*             103: delta ray  generation secondaries                   *
*             104: pair production secondaries                         *
*             105: bremsstrahlung  secondaries                         *
*             110: decay products                                      *
*     Icode = 20x: call from Emfsco                                    *
*             208: bremsstrahlung secondaries                          *
*             210: Moller secondaries                                  *
*             212: Bhabha secondaries                                  *
*             214: in-flight annihilation secondaries                  *
*             215: annihilation at rest   secondaries                  *
*             217: pair production        secondaries                  *
*             219: Compton scattering     secondaries                  *
*             221: photoelectric          secondaries                  *
*             225: Rayleigh scattering    secondaries                  *
*             237: mu pair     production secondaries                  *
*     Icode = 30x: call from Kasneu                                    *
*             300: interaction secondaries                             *
*     Icode = 40x: call from Kashea                                    *
*             400: delta ray  generation secondaries                   *
*  For all interactions secondaries are put on GENSTK common (kp=1,np) *
*  but for KASHEA delta ray generation where only the secondary elec-  *
*  tron is present and stacked on FLKSTK common for kp=npflka          *
*                                                                      *
*======================================================================*
      ENTRY USDRAW ( ICODE, MREG, XSCO, YSCO, ZSCO )
      OPEN(UNIT=67, FILE = 'pg_produced.txt', STATUS='UNKNOWN')
      OPEN(UNIT=68, FILE = 'gamma_produced.txt', STATUS='UNKNOWN')
      OPEN(UNIT=69, FILE = 'FN_produced.txt', STATUS='UNKNOWN')
      OPEN(UNIT=70, FILE = 'Neutrons_produced.txt', STATUS='UNKNOWN')
      OPEN(UNIT=71, FILE = 'residual.txt', STATUS='UNKNOWN')
      OPEN(UNIT=72, FILE = 'mreg.txt', STATUS='UNKNOWN')

* ****Parameter definitions****                                        *
*                                                                      *
* ICODE = interaction code. Important icodes are 101 for inelastic     *
* interaction, 100 for elastic interaction, 106 for de-excitation, 300 *
* for low energy neutron interaction                                   *

* NCASE = history number. For number of primaries = 1000, NCASE will   *
* range from 1 to 1000                                                 *

* MREG = current region. In my simulations, PMMA phantom is region     *
* number 3. 

* JTRACK = id of the current particle being tracked. If jtrack = 1 it  *
* means that the particle that is being tracked is a proton.           *
* The combination JTRACK.EQ.1 and ICODE.EQ.101 means the current       *       
* interaction was inelastic and caused by a proton.    
*
* NP = Number of secondaries. This is specific to the FLUKA stack 
* called GENSTK, which is the stack where secondary particles are being*
* saved. However, information about the residual nucleus is not saved  * 
* in this stack, but in the FLUKA stack named FHEAVY. If one wishes to *
* loop over FHEAVY, one should use NPHEAV instead of NP. See FHEAVY and* 
* GENSTK files for further information.                                *

* Tki(IP) = kinetic energy of the IPth secondary.                      *
* XSCO,YSCO,ZSCO = X,Y,Z coordinate of the interaction                 * 
* Cxr(IP),Cyr(IP),Czr(IP) = x,y,z cosines of the angle the IPth        * 
* particle was emitted with.                                           *


*Use ISPUSR for saving integer values: ICODE, NCASE, JTRACK
*USE SPAUSR for saving floats

***** START ADDED BY ANNA IN USDRAW*****************************
*nedenfor er det ok foreløpig. Burde inkludere noe om JTRACK

* If the current region is 3 and there has been an inelastic interaction, 
* save information about the interacting nucleus. Ichtar, Ibtar are 
* parameters from FHEAVY and denote the A and Z of the interacting nucleus
*      IF(MREG .EQ. 3) THEN
        IF(ICODE.EQ.101) THEN
            ISPUSR(7) = Ichtar
            ISPUSR(8) = Ibtar
        END IF
*      END IF

*The USRDCI function is used to find information about the residual nucleus
*      IF(MREG .EQ. 3) THEN
        IF(ICODE.EQ.101  .OR. ICODE.EQ.106) THEN
* Looping over all the secondaries created in the interaction.
* If the number of secondaries are 3, then IP ranges from 1 to 3. 
* Tki(IP) = kinetic energy of the IPth secondary. XSCO,YSCO,ZSCO. 
* ISPUSR(9) is in this case the icode of the previous interaction. 
* Could be nice to have to have an overview over if the de-excitation 
* is a result of a nucleus decaying (99% of the cases) or if it is a 
* result of electron de-excitation after a photoelectric effect event (i.e. characteristic x-rays).  
            DO IP = 1, NP
                IF(KPART(IP) .EQ. 7) THEN
                    CALL USRDCI(ILOFLK(0),IONA,IONZ,IONM)
* WRITE 8 integers (I4), followed by 7 floats (6 decimals, 10 characters space)
                    WRITE(67,'(3I7,1X,5I3,1X,7F11.6)')
     &                 NCASE,ICODE,ISPUSR(9),JTRACK,
     &                 IONZ,IONA,ISPUSR(7),ISPUSR(8),
     &                 Tki(IP),XSCO,YSCO,ZSCO,
     &                 Cxr(IP),Cyr(IP),Czr(IP)

* Saving information about the particles. This is used in the boundary crossing code 
* bxdraw (further up in this document)
                    ISPUSR(1) = NCASE
                    ISPUSR(2) = ICODE
                    ISPUSR(3) = JTRACK
                    ISPUSR(4) = 1

                    SPAUSR(1) = Tki(IP)
                    SPAUSR(2) = XSCO
                    SPAUSR(3) = YSCO
                    SPAUSR(4) = ZSCO
                    SPAUSR(5) = Cxr(IP)
                    SPAUSR(6) = Cyr(IP)
                    SPAUSR(7) = Czr(IP)

                    ISPUSR(5) = IONZ
                    ISPUSR(6) = IONA
                ENDIF 
            END DO
* For Kristians peace of mind hehe
        ELSE IF (ICODE .NE. 101 .AND. ICODE .NE. 106) THEN
* If gamma is emitted, but is not coming from an de-exciting nucleus or directly from 
* an inelastic interaction (icode = 101). Most of these photons come from bremsstrahlung 
* radiation (icode = 208) and compton scattering (icode = 219). 
            DO IP = 1, NP
                IF(KPART(IP) .EQ. 7) THEN

                    CALL USRDCI(ILOFLK(0),IONA,IONZ,IONM)
* Write 3 integers, followed by 7 floats. First integer (NCASE) can have up to 7 digits. 
                    WRITE(68,'(I7,1X,2I3,1X,1X,F10.8,6F11.6)')
     &                 NCASE,ICODE,JTRACK,Tki(IP),
     &                 XSCO,YSCO,ZSCO,
     &                 Cxr(IP),Cyr(IP),Czr(IP)
                    
                    ISPUSR(1) = NCASE
                    ISPUSR(2) = ICODE
                    ISPUSR(3) = JTRACK
                    IF (ISPUSR(4) .EQ. 1) THEN
                        ISPUSR(4) = 1
                    END IF 

                    SPAUSR(1) = Tki(IP)
                    SPAUSR(2) = XSCO
                    SPAUSR(3) = YSCO
                    SPAUSR(4) = ZSCO
                    SPAUSR(5) = Cxr(IP)
                    SPAUSR(6) = Cyr(IP)
                    SPAUSR(7) = Czr(IP)


                ENDIF 
            END DO
        END IF
*      END IF

* Saving the "old-icode" in the ISPUSR(9). See comment further up. 
*      IF(MREG .EQ. 3) THEN
        ISPUSR(9) = ICODE
*      END IF

*Procution of neutrons by inelastic nuclear interactions by protons!
*      IF(MREG .EQ. 3) THEN
        IF(ICODE.EQ.101 .AND. JTRACK.EQ.1) THEN
            DO IP = 1, NP
                IF(KPART(IP) .EQ. 8) THEN
* Write 3 integers, followed by 7 floats. First integer (NCASE) can have up to 7 digits. 
                  WRITE(69,'(I7,1X,2I3,1X,7F10.6)')
     &                 NCASE,ICODE,JTRACK,Tki(IP),
     &                 XSCO,YSCO,ZSCO,
     &                 Cxr(IP),Cyr(IP),Czr(IP)
                  WRITE(72,*) MREG

                  ISPUSR(1) = NCASE
                  ISPUSR(2) = ICODE
                  ISPUSR(3) = JTRACK

                  SPAUSR(1) = Tki(IP)
                  SPAUSR(2) = XSCO
                  SPAUSR(3) = YSCO
                  SPAUSR(4) = ZSCO
                  SPAUSR(5) = Cxr(IP)
                  SPAUSR(6) = Cyr(IP)
                  SPAUSR(7) = Czr(IP)
                END IF
            END DO
        ELSE IF (ICODE .NE. 101 .AND. JTRACK.NE.1) THEN
            IF(ICODE.NE.300) THEN
* production of neutrons from other interaction codes (for instance 100 for elastic collision). 
* icode = 300 handled separetly further down
* NB: it is only interesting to save the first scatter interaction for icode = 300
            DO IP = 1, NP
                EKPART=ETRACK-AM(JTRACK)
                IF (KPART(IP) .EQ. 8 .AND. EKPART.GT.1E-6) THEN
* Write 3 integers, followed by 7 floats. First integer (NCASE) can have up to 7 digits. 
                  WRITE(70,'(I7,1X,2I3,1X,F10.8,1X,6F10.6)')
     &                 NCASE,ICODE,JTRACK,Tki(IP),
     &                 XSCO,YSCO,ZSCO,
     &                 Cxr(IP),Cyr(IP),Czr(IP)
                  ISPUSR(1) = NCASE
                  ISPUSR(2) = ICODE
                  ISPUSR(3) = JTRACK

                  SPAUSR(1) = Tki(IP)
                  SPAUSR(2) = XSCO
                  SPAUSR(3) = YSCO
                  SPAUSR(4) = ZSCO
                  SPAUSR(5) = Cxr(IP)
                  SPAUSR(6) = Cyr(IP)
                  SPAUSR(7) = Czr(IP)
                END IF
            END DO
            END IF
        END IF
*      END IF

*      IF (MREG .EQ. 3) THEN
        IF (ICODE.EQ.300 .AND. JTRACK.EQ.8) THEN
            IF(ISPUSR(10).NE.NCASE) THEN
            DO IP = 1, NP
            IF(KPART(IP) .EQ. 8) THEN
                WRITE(70,'(I7,1X,2I3,1X,F10.8,1X,6F10.6)')
     &                 NCASE,ICODE,JTRACK,Tki(IP),
     &                 XSCO,YSCO,ZSCO,
     &                 Cxr(IP),Cyr(IP),Czr(IP)
            END IF 
            END DO
            END IF
        END IF
*      END IF


*      IF (ICODE .EQ. 101 .AND. MREG.EQ.3) THEN
      IF (ICODE .EQ. 101) THEN
* Loop over secondaries stored in fheavy. 7-12 equals heavyion
      DO IP = 1, NPHEAV
      WRITE(71,*) ibheav(KHEAVY(IP)),icheav(KHEAVY(IP)),NCASE,MREG
      END DO
      END IF

* Save old ncase for checking low-energy neutron scattering. 
*      IF (ICODE .EQ. 300 .AND. MREG.EQ.3 .AND. JTRACK.EQ.8) THEN
      IF (ICODE .EQ. 300 .AND. JTRACK.EQ.8) THEN
      DO IP = 1, NP
        IF (KPART(IP) .EQ. 8) THEN
        ISPUSR(10) = NCASE
        END IF
      END DO
      END IF






* 
* Np = total number of secondaries *
* Kpart (ip) = (Paprop) id of the ip_th secondary *
* Cxr (ip) = x-axis direction cosine of the ip_th secondary *
* Tki (ip) = laboratory kinetic energy of ip_th secondary (GeV)*
* Wei (ip) = statistical weight of the ip_th secondary *
* etc. (look up the full list in $FLUPRO/flukapro/(GENSTK) 
***** END ADDED BY ANNA*****************************

      IF ( .NOT. LFCOPE ) THEN
         LFCOPE = .TRUE.
         IF ( KOMPUT .EQ. 2 ) THEN
            FILNAM = '/'//CFDRAW(1:8)//' DUMP A'
         ELSE
            FILNAM = CFDRAW
         END IF
         OPEN ( UNIT = IODRAW, FILE = FILNAM, STATUS = 'NEW', FORM =
     &          'UNFORMATTED' )
      END IF
* No output by default:
      RETURN
      CLOSE(67)
      CLOSE(68)
      CLOSE(69)
      CLOSE(70)
      CLOSE(71)
      CLOSE(72)
  
*=== End of subrutine Mgdraw ==========================================*    
      END
